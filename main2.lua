package.path = package.path .. ";./json/json.lua"

local desired_species = -1
local atkdef
local spespc
local species
local item = 0
local shinyvalue = 0
local flaskServerURL = "http://127.0.0.1:5000/update_data"
local printedMessage = false
local enemy_addr
local daytime
initialX, initialY = memory.readbyte(0xdcb8), memory.readbyte(0xdcb7)
mapgroup, mapnumber = memory.readbyte(0xdcb5), memory.readbyte(0xdcb6)
local version = memory.readbyte(0x141)
local region = memory.readbyte(0x142)
local encounterCount
local framesInDirection = 0
local maxFramesInDirection = 1
local highestSpeSpc = 0
local highestAtkDef = 0
json = require("json")
mem = require("memory")
mem.SetRomBankAddress("Crystal")
input = {}
actions = {"B", "Right", "Right", "Down", "A","A"}
currentActionIndex = 1
framesInAction = 0
framesPerAction = 1
input2 = {}
actions2 = {"Right", "Up", "Left", "Down"}
currentActionIndex2 = 1
framesInAction2 = 0
framesPerAction2 = 1

if version == 0x54 then
    if region == 0x44 or region == 0x46 or region == 0x49 or region == 0x53 then
        enemy_addr = 0xd20c
    elseif region == 0x45 then
        enemy_addr = 0xd20c
    elseif region == 0x4A then
        enemy_addr = 0xd23d
    end
else
    print("Script stopped")
    return
end

local dv_flag_addr = enemy_addr + 0x21
local species_addr = enemy_addr + 0x22
local item_addr = enemy_addr - 0x05
local daytime_addr = 0xd269

local LoadBattleMenuAddr = mem.BankAddressToLinear(0x9, 0x4EF2)

function shiny(atkdef, spespc)
    if spespc == 0xAA then
        if atkdef == 0x2A or atkdef == 0x3A or atkdef == 0x6A or atkdef == 0x7A or atkdef == 0xAA or atkdef == 0xBA or atkdef == 0xEA or atkdef == 0xFA then
            shinyvalue = 1
            return true
        end
    end
    return false
end

function send_data_to_flask(highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc, atkdef, daytime_value, map)
    local daytime_string
    local map
    daytime_value = memory.readbyte(daytime_addr)

    local data = {
        highestAtkDef = highestAtkDef,
        highestSpeSpc = highestSpeSpc,
        item = item,
        shinyvalue = shinyvalue,
        species = species,
        spespc = spespc,
        atkdef = atkdef,
        daytime = daytime_string,
    }

    local concatenated_data = highestAtkDef .. "," .. highestSpeSpc .. "," .. item .. "," .. shinyvalue .. "," .. species .. "," .. spespc .. "," .. atkdef .. "," .. daytime_value .. "," .. mapgroup .. "," .. mapnumber

    -- Send the concatenated data as the payload
    -- print(concatenated_data)
    -- local status_code, response_body = comm.httpPost(flaskServerURL, concatenated_data)
end

function press_button(btn)
    input = {[btn]=true}
    for i=1,4 do -- Hold button for 4 frames (make sure the game registers it)
        joypad.set(input)
        emu.frameadvance()
    end
    emu.frameadvance() -- Add one frame buffer so consecutive button presses don't blend together
end

local have_battle_controls = false
mem.RegisterROMHook(LoadBattleMenuAddr, function()
    --print("Battle menu loaded")
    have_battle_controls = true
end, "Detect Battle Menu")

while true do
    emu.frameadvance()

    if memory.readbyte(species_addr) == 0 then
        have_battle_controls = false

        for i=1,8,1 do
            emu.frameadvance()
            joypad.set({B=true})
        end


        local currentX, currentY = memory.readbyte(0xdcb8), memory.readbyte(0xdcb7)

        if currentX ~= initialX or currentY ~= initialY and memory.readbyte(species_addr) == 0 then
            -- Navigate back to initial position
            local deltaX = initialX - currentX
            local deltaY = initialY - currentY

            for _ = 1, math.abs(deltaX) do
                emu.frameadvance()
                joypad.set({Up = false, Right = (deltaX > 0), Down = false, Left = (deltaX < 0)})
                emu.frameadvance()
                if memory.readbyte(species_addr) ~= 0 then
                    emu.frameadvance()
                    break
                end
            end

            for _ = 1, math.abs(deltaY) do
                emu.frameadvance()
                joypad.set({Up = (deltaY < 0), Right = false, Down = (deltaY > 0), Left = false})
                emu.frameadvance()
                if memory.readbyte(species_addr) ~= 0 then
                    emu.frameadvance()
                    break
                end
            end
        else
            joypad.set({Right=true})
            emu.frameadvance()
            joypad.set({Right=false})
            joypad.set({Left=true})
            emu.frameadvance()
            joypad.set({Left=false})
            joypad.set({Down=true})
            emu.frameadvance()
            joypad.set({Down=false})
            joypad.set({Up=true})
            emu.frameadvance()
            joypad.set({Up=false})

        end

    else
        while memory.readbyte(dv_flag_addr) ~= 0x01 do
            emu.frameadvance()
            press_button("B")
        end

        item = memory.readbyte(item_addr)
        atkdef = memory.readbyte(enemy_addr)
        spespc = memory.readbyte(enemy_addr + 1)
        highestAtkDef = math.max(highestAtkDef, atkdef)
        highestSpeSpc = math.max(highestSpeSpc, spespc)
        species = memory.readbyte(species_addr)



        if shiny(atkdef, spespc) then
            shinyvalue = 1
            send_data_to_flask(highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc, atkdef)
            break
        end

        send_data_to_flask(highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc, atkdef)
    end

    if memory.readbyte(species_addr) ~= 0 then

        while not have_battle_controls do
            emu.frameadvance()
            currentActionIndex = 1
            press_button("B")
        end

        local currentAction = actions[currentActionIndex]

        press_button(currentAction)

        framesInAction = framesInAction + 1

        if framesInAction >= framesPerAction then
            framesInAction = 0
            currentActionIndex = (currentActionIndex % #actions) + 1
            emu.frameadvance()
        end
    end
end
