local config = require("config")

local ui = {}

-- Returns the image, x/y offsets, and a scale factor.
local function resize_keep_width(image)
    local iw, ih = image:getWidth(), image:getHeight()
    local new_width = config.SCREEN_WIDTH
    local scale = new_width / iw
    local new_height = ih * scale
    local offset_y = 0
    if new_height > config.SCREEN_HEIGHT then
        offset_y = (new_height - config.SCREEN_HEIGHT) / 2
    end
    return image, 0, -offset_y, scale
end

local function resize_fit_to_screen(image)
    local iw, ih = image:getWidth(), image:getHeight()
    local sw, sh = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
    local aspect = iw / ih
    local new_width, new_height, offset_x, offset_y, scale
    if sw/sh > aspect then
        new_height = sh
        new_width = sh * aspect
    else
        new_width = sw
        new_height = sw / aspect
    end
    scale = new_width / iw
    offset_x = (sw - new_width) / 2
    offset_y = (sh - new_height) / 2
    return image, offset_x, offset_y, scale
end

function ui.update_ui(games, current_game_index, keep_width_mode)
    if #games == 0 then
        return 0, 0, nil, 0, 1
    end

    local game = games[current_game_index]
    local cover = game.cover
    local image = nil
    if love.filesystem.getInfo(cover) then
        image = love.graphics.newImage(cover)
    end
    local fade_alpha = 0
    if not image then
        return 0, 0, nil, 0, 1
    end

    local x, y, scale
    if keep_width_mode then
        image, x, y, scale = resize_keep_width(image)
    else
        image, x, y, scale = resize_fit_to_screen(image)
    end

    return x, y, image, fade_alpha, scale
end

return ui
