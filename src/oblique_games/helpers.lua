local json = require("json")  -- make sure you have a JSON module installed
local helpers = {}

function helpers.load_image(path, size)
    if not love.filesystem.getInfo(path) then
        return nil
    end
    local image = love.graphics.newImage(path)
    -- Optionally store intended size (you can adjust drawing scale as needed)
    image.scaledWidth = size and size.width or image:getWidth()
    image.scaledHeight = size and size.height or image:getHeight()
    return image
end

function helpers.load_metadata(metadata_path)
    if not love.filesystem.getInfo(metadata_path) then
        return {}
    end
    local content = love.filesystem.read(metadata_path)
    local ok, metadata = pcall(json.decode, content)
    if ok and type(metadata) == "table" then
        return metadata
    else
        return {}
    end
end

function helpers.process_game(game_path, game_name)
    local metadata_file = game_path.."/metadata.json"
    local cover_file = game_path.."/cover.png"
    if not love.filesystem.getInfo(metadata_file) or not love.filesystem.getInfo(cover_file) then
        return nil
    end
    local metadata = helpers.load_metadata(metadata_file)
    local branding_data = metadata.branding_data or {}
    if type(branding_data) == "string" then
        branding_data = {}
    end
    return {
        type = metadata.game_type or "Unknown",
        name = metadata.name or game_name,
        model = metadata.model or "Unknown",
        metadata = metadata,
        branding_data = branding_data,
        cover = cover_file,
    }
end

function helpers.load_games(root_dir, shuffle)
    if not love.filesystem.getInfo(root_dir) then
        return {}
    end
    local games = {}
    local items = love.filesystem.getDirectoryItems(root_dir)
    for _, game_type in ipairs(items) do
        local game_type_path = root_dir.."/"..game_type
        if love.filesystem.getInfo(game_type_path, "directory") then
            local game_names = love.filesystem.getDirectoryItems(game_type_path)
            for _, game_name in ipairs(game_names) do
                local game_path = game_type_path.."/"..game_name
                local game_data = helpers.process_game(game_path, game_name)
                if game_data then
                    table.insert(games, game_data)
                end
            end
        end
    end
    if shuffle then
        for i = #games, 2, -1 do
            local j = math.random(i)
            games[i], games[j] = games[j], games[i]
        end
    end
    return games
end

return helpers
