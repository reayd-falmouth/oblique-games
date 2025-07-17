local config = require("config")
local SoundManager = {}
SoundManager.__index = SoundManager

function SoundManager:new()
    local self = setmetatable({}, SoundManager)
    self.background_hum = love.audio.newSource(config.ASSETS_DIR.."/audio/hum.ogg", "static")
    self.startup_sound  = love.audio.newSource(config.ASSETS_DIR.."/audio/startup.ogg", "static")
    self.button_sound   = love.audio.newSource(config.ASSETS_DIR.."/audio/button.ogg", "static")
    self.buzz_sound     = love.audio.newSource(config.ASSETS_DIR.."/audio/buzz.ogg", "static")
    self.click_sound    = love.audio.newSource(config.ASSETS_DIR.."/audio/click.ogg", "static")
    self.pause_menu_music = love.audio.newSource(config.ASSETS_DIR.."/audio/music.ogg", "static")

    self.background_hum:setVolume(0.5)
    self.startup_sound:setVolume(1.0)
    self.button_sound:setVolume(1.0)
    self.buzz_sound:setVolume(1.0)
    self.click_sound:setVolume(1.0)
    self.pause_menu_music:setVolume(0.0)  -- starts muted
    self.pause_music_active = false

    return self
end

function SoundManager:play_background()
    self.background_hum:setLooping(true)
    love.audio.play(self.background_hum)
end

function SoundManager:stop_background()
    self.background_hum:stop()
end

function SoundManager:play_startup()
    love.audio.play(self.startup_sound)
end

function SoundManager:play_button_sound()
    self.button_sound:stop()
    love.audio.play(self.button_sound)
end


function SoundManager:play_buzz_sound()
    self.buzz_sound:stop()
    love.audio.play(self.buzz_sound)
end

function SoundManager:play_click_sound()
    love.audio.play(self.click_sound)
end

function SoundManager:play_pause_menu_music(fade_ms)
    fade_ms = fade_ms or 2000
    if not self.pause_music_active then
        self.pause_menu_music:setLooping(true)
        love.audio.play(self.pause_menu_music)
        self.pause_menu_music:setVolume(0.1)
        self.pause_music_active = true
    else
        self.pause_menu_music:setVolume(0.1)
    end
end

function SoundManager:mute_pause_menu_music()
    self.pause_menu_music:setVolume(0.0)
end

return SoundManager
