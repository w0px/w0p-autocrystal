package.path = package.path .. ";./json/json.lua;./luasocket/src/?.lua"


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

local version = memory.readbyte(0x141)
local region = memory.readbyte(0x142)
local encounterCount 
local framesInDirection = 0
local maxFramesInDirection = 32
local highestSpeSpc = 0
local highestAtkDef = 0
json = require("json")
socket = require("socket")
socket.http = require("socket.http")
input = {}
actions = {"B","Right","Right","Down", "A"}
currentActionIndex = 1
framesInAction = 0
framesPerAction = 2
input2 = {}
actions2 = {"Right", "Up", "Left", "Down"}
currentActionIndex2 = 1
framesInAction2 = 0
framesPerAction2 = 3
local daytime_strings = {"Day", "Morning", "Night"}

-- version check
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



function send_data_to_flask(highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc, atkdef, daytime_value)
    local daytime_string
    daytime_value = memory.readbyte(daytime_addr)

    if daytime_value == 0 then
        daytime_string = "Day"
    elseif daytime_value == 1 then
        daytime_string = "Morning"
    elseif daytime_value == 2 then
        daytime_string = "Night"
    else
        daytime_string = "Unknown"
        daytime_value = -1  -- Set a default value for the unknown case
    end

    local data = {
        highestAtkDef = highestAtkDef,
        highestSpeSpc = highestSpeSpc,
        item = item,
        shinyvalue = shinyvalue,
        species = species,
        spespc = spespc,
        atkdef = atkdef,
        daytime = daytime_string
    }

    -- Concatenate variables into a single string
    local concatenated_data = highestAtkDef .. "," .. highestSpeSpc .. "," .. item .. "," .. shinyvalue .. "," .. species .. "," .. spespc .. "," .. atkdef .. "," .. daytime_value

    -- Send the concatenated data as the payload
    local status_code, response_body = comm.httpPost(flaskServerURL, concatenated_data)

    -- ...
end

while true do
    emu.frameadvance()
    
    if memory.readbyte(species_addr) == 0 then
        local currentAction = actions2[currentActionIndex2]

        input[currentAction] = true
        emu.frameadvance()
        joypad.set(input)
        emu.frameadvance()
        input[currentAction] = false
        

        framesInAction2 = framesInAction2 + 1

        if framesInAction2 >= framesPerAction2 then
            framesInAction2 = 0
            currentActionIndex2 = (currentActionIndex2 % #{"Up", "Right", "Down", "Left"}) + 1
            emu.frameadvance()
            

       
    end
    else
        
                    
        if desired_species > 0 and desired_species ~= species then
            
        else
            while memory.readbyte(dv_flag_addr) ~= 0x01 do
                emu.frameadvance()
            end

            item = memory.readbyte(item_addr)
            atkdef = memory.readbyte(enemy_addr)
            spespc = memory.readbyte(enemy_addr + 1)
            highestAtkDef = math.max(highestAtkDef, atkdef)
            highestSpeSpc = math.max(highestSpeSpc, spespc)
            species = memory.readbyte(species_addr)
            

            
            
            

            if shiny(atkdef, spespc) then
                print("Shiny found!!")
                shinyvalue = 1
                local shinyInfo = "Shiny found!!"
                send_data_to_flask(highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc,atkdef)
                break
            
            end

            send_data_to_flask(highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc,atkdef)
            
        end
    end 

    if memory.readbyte(species_addr) ~= 0 then

        for i=1,48,1 do
            emu.frameadvance()
        end

        local currentAction = actions[currentActionIndex]

        input[currentAction] = true
        joypad.set(input)
        emu.frameadvance()
        input[currentAction] = false
				
        framesInAction = framesInAction + 1

        if framesInAction >= framesPerAction then
            framesInAction = 0
            currentActionIndex = (currentActionIndex % #actions) + 1
            emu.frameadvance()
        end
        
    end
end
