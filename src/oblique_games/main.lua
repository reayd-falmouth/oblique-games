local config = require("config")
local helpers = require("helpers")
local SoundManager = require("sound")
local ShaderRenderer = require("shader")
local fontModule = require("font")
local ui = require("ui")

local Game = {}
Game.__index = Game

if not table.unpack then
    table.unpack = unpack
end

function Game:new()
    local self = setmetatable({}, Game)
    love.window.setMode(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, {resizable = false})
    love.window.setTitle(config.BROWSER_TITLE)
    self.paused = false
    self.paused_page = 1

    self.pause_menu = helpers.load_games(config.ASSETS_DIR.."/img", false)
    self.sound_manager = SoundManager:new()
    self.sound_manager:play_background()
    self.sound_manager:play_startup()
    self.games = helpers.load_games(config.ASSETS_DIR.."/games", true)
    self.total_games = #self.games
    self.current_game_index = 1
    self.fonts = fontModule.load_fonts()
    self.random_ordering_enabled = true
    self.order_mode = "random"

    local x, y, bg, fade, scale = ui.update_ui(self.games, self.current_game_index, true)
    self.background_x = x
    self.background_y = y
    self.background_image = bg
    self.fade_alpha = fade
    self.bg_scale = scale

    -- Create a canvas for final post-processing.
    self.canvas = love.graphics.newCanvas(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    self.shader = ShaderRenderer:new(true)
    return self
end

function Game:draw_background()
    love.graphics.setColor(config.BLACK)
    love.graphics.rectangle("fill", 0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    if self.background_image then
        self.fade_alpha = math.min(150, self.fade_alpha + config.FADE_SPEED)
        love.graphics.setColor(1, 1, 1, self.fade_alpha / 255)
        love.graphics.draw(self.background_image, self.background_x, self.background_y, 0, self.bg_scale, self.bg_scale)
        love.graphics.setColor(1, 1, 1, 1)
    end
end

function Game:get_wrapped_text_height(text, font, max_width)
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

    local lines = wrap_text(text, font, max_width)
    return #lines * font:getHeight()
end

function Game:draw_game_info()
    if #self.games == 0 then return end

    local game = self.games[self.current_game_index]
    if self.paused then
        game = self.pause_menu[self.paused_page] or game
    end

    local metadata = game.metadata or {}
    local title = metadata.name or "Unknown Game"
    local game_type = "Game Type: " .. (game.type or "Unknown")
    local model = "Model: " .. (game.model or "Unknown")
    local prompt = "Prompt: " .. (metadata.task or "Unknown")
    local branding_data = game.branding_data or {}
    local short_description = branding_data.short_description or "No description available"

    local game_info = {
        { "title", title, false },
        { "metadata", game_type, false },
        { "metadata", model, false },
        { "tags", prompt, false },
        { "metadata", short_description, true },
    }

    local x_start = 50
    local y_start = 50
    local line_spacing = 10
    local extra_spacing = 40
    local max_width = config.SCREEN_WIDTH - 100

    for _, info in ipairs(game_info) do
        local font_key, text, extra_space = table.unpack(info)
        local font = self.fonts[font_key] or self.fonts.metadata
        if extra_space then
            y_start = y_start + extra_spacing
        end
        fontModule.render_wrapped_text(text, x_start, y_start, font, max_width, config.TRANSLUCENT_BLACK)
        y_start = y_start + self:get_wrapped_text_height(text, font, max_width) + line_spacing
    end

    local tags_info = "Tags: " .. table.concat(branding_data.tags or {}, ", ")
    fontModule.render_wrapped_text(tags_info, 50, config.SCREEN_HEIGHT - 100, self.fonts.tags, max_width, config.TRANSLUCENT_BLACK)

    local page_info = self.current_game_index .. " of " .. self.total_games
    if self.paused then
        page_info = "? of ?"
    end
    fontModule.render_wrapped_text(page_info, config.SCREEN_WIDTH - 150, config.SCREEN_HEIGHT - 50, self.fonts.metadata, max_width, config.TRANSLUCENT_BLACK)
end

function Game:update_ui()
    local x, y, bg, fade, scale = ui.update_ui(self.games, self.current_game_index, true)
    self.background_x = x
    self.background_y = y
    self.background_image = bg
    self.fade_alpha = fade
    self.bg_scale = scale
end

function Game:handle_key(key, isctrl)
    if key == "p" then
        self.paused = not self.paused
        self.sound_manager:play_click_sound()
        if self.paused then
            self.paused_page = 2
            self.sound_manager:play_pause_menu_music()
            local x, y, bg, fade, scale = ui.update_ui(self.pause_menu, self.paused_page, true)
            self.background_x, self.background_y, self.background_image, self.fade_alpha, self.bg_scale = x, y, bg, fade, scale
        else
            self.sound_manager:mute_pause_menu_music()
            local x, y, bg, fade, scale = ui.update_ui(self.games, self.current_game_index, true)
            self.background_x, self.background_y, self.background_image, self.fade_alpha, self.bg_scale = x, y, bg, fade, scale
        end
    elseif key == "c" then
        self.paused = not self.paused
        self.paused_page = 1
        self.sound_manager:play_click_sound()
        if self.paused then
            self.sound_manager:play_pause_menu_music()
            local x, y, bg, fade, scale = ui.update_ui(self.pause_menu, self.paused_page, true)
            self.background_x, self.background_y, self.background_image, self.fade_alpha, self.bg_scale = x, y, bg, fade, scale
        else
            self.sound_manager:mute_pause_menu_music()
            local x, y, bg, fade, scale = ui.update_ui(self.games, self.current_game_index, true)
            self.background_x, self.background_y, self.background_image, self.fade_alpha, self.bg_scale = x, y, bg, fade, scale
        end
    elseif not self.paused then
        if key == "right" and isctrl then
            if not self.random_ordering_enabled then
                local current_name = self.games[self.current_game_index].metadata[self.order_mode] or ""
                if current_name ~= "" then
                    local current_letter = current_name:sub(1,1):lower()
                    local new_index = self.current_game_index
                    for i = self.current_game_index + 1, #self.games do
                        local name = self.games[i].metadata[self.order_mode] or ""
                        if name ~= "" and name:sub(1,1):lower() ~= current_letter then
                            new_index = i
                            break
                        end
                    end
                    self.current_game_index = new_index
                    self.sound_manager:play_button_sound()
                    self:update_ui()
                    return
                end
            end
        elseif key == "right" then
            self.current_game_index = (self.current_game_index % #self.games) + 1
            self.sound_manager:play_button_sound()
        elseif key == "left" and isctrl then
            if not self.random_ordering_enabled then
                local current_name = self.games[self.current_game_index].metadata[self.order_mode] or ""
                if current_name ~= "" then
                    local current_letter = current_name:sub(1,1):lower()
                    local new_index = self.current_game_index
                    for i = self.current_game_index - 1, 1, -1 do
                        local name = self.games[i].metadata[self.order_mode] or ""
                        if name ~= "" and name:sub(1,1):lower() ~= current_letter then
                            new_index = i
                            break
                        end
                    end
                    self.current_game_index = new_index
                    self.sound_manager:play_button_sound()
                    self:update_ui()
                    return
                end
            end
        elseif key == "left" then
            self.current_game_index = ((self.current_game_index - 2) % #self.games) + 1
            self.sound_manager:play_button_sound()
        elseif key == "o" then
            if self.order_mode == "random" then
                self.order_mode = "name"
                self.random_ordering_enabled = false
                table.sort(self.games, function(a, b)
                    local nameA = (a.metadata.name or ""):lower()
                    local nameB = (b.metadata.name or ""):lower()
                    return nameA < nameB
                end)
            elseif self.order_mode == "name" then
                self.order_mode = "game_type"
                self.random_ordering_enabled = false
                table.sort(self.games, function(a, b)
                    local nameA = (a.metadata.game_type or ""):lower()
                    local nameB = (b.metadata.game_type or ""):lower()
                    return nameA < nameB
                end)
            else
                self.order_mode = "random"
                self.random_ordering_enabled = true
                for i = #self.games, 2, -1 do
                    local j = math.random(i)
                    self.games[i], self.games[j] = self.games[j], self.games[i]
                end
            end
            self.current_game_index = 1
            self.total_games = #self.games
            self.sound_manager:play_click_sound()
        else
            self.sound_manager:play_buzz_sound()
        end
        self:update_ui()
    end
end

local game = nil

function love.load()
    math.randomseed(os.time())
    game = Game:new()
end

function love.update(dt)
end

function love.draw()
    -- Draw scene onto the canvas first (no shader).
    love.graphics.setCanvas(game.canvas)
    love.graphics.clear(0, 0, 0, 1)
    love.graphics.setShader(nil)
    game:draw_background()
    game:draw_game_info()
    love.graphics.setCanvas()

    -- Update the shader uniform using the underlying shader.
    game.shader.shader:send("texSize", {game.canvas:getWidth(), game.canvas:getHeight()})

    -- Now apply the shader to the final canvas.
    game.shader:render(function()
        love.graphics.draw(game.canvas, 0, 0)
    end)
end

function love.keypressed(key, scancode, isrepeat)
    local isctrl = love.keyboard.isDown("lctrl") or love.keyboard.isDown("rctrl")
    game:handle_key(key, isctrl)
end
