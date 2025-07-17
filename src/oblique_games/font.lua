local config = require("config")
local fontModule = {}

-- Custom text-wrapping function that splits text into lines based on max_width.
local function wrap_text(text, font, max_width)
    local words = {}
    for word in text:gmatch("%S+") do
        table.insert(words, word)
    end

    local lines = {}
    local current_line = ""
    for _, word in ipairs(words) do
        local test_line = (current_line == "") and word or (current_line .. " " .. word)
        if font:getWidth(test_line) > max_width then
            table.insert(lines, current_line)
            current_line = word
        else
            current_line = test_line
        end
    end
    if current_line ~= "" then
        table.insert(lines, current_line)
    end
    return lines
end

function fontModule.load_fonts()
    local font_path = config.ASSETS_DIR.."/fonts/m6x11.ttf"
    return {
        title = love.graphics.newFont(font_path, 48),
        description = love.graphics.newFont(font_path, 28),
        detailed_description = love.graphics.newFont(font_path, 14),
        metadata = love.graphics.newFont(font_path, 24),
        tags = love.graphics.newFont(font_path, 20),
    }
end

function fontModule.render_wrapped_text(text, x, y, font, max_width, box_fill)
    love.graphics.setFont(font)
    local lines = wrap_text(text, font, max_width)
    local line_height = font:getHeight()
    local text_height = #lines * line_height

    -- Draw background box with padding
    love.graphics.setColor(box_fill)
    love.graphics.rectangle("fill",
        x - config.TEXT_BOX_PADDING,
        y - config.TEXT_BOX_PADDING,
        max_width + config.TEXT_BOX_PADDING * 2,
        text_height + config.TEXT_BOX_PADDING * 2)

    love.graphics.setColor(1, 1, 1, 1)
    -- Draw each line of text
    for i, line in ipairs(lines) do
        love.graphics.print(line, x, y + (i - 1) * line_height)
    end
end

return fontModule
