local config = require("config")
local ShaderRenderer = {}
ShaderRenderer.__index = ShaderRenderer

function ShaderRenderer:new(enabled)
    local self = setmetatable({}, ShaderRenderer)
    self.enabled = (enabled ~= false)
    if self.enabled then
        local vertex_code = love.filesystem.read(config.ASSETS_DIR.."/shaders/love/vertex.glsl")
        local pixel_code = love.filesystem.read(config.ASSETS_DIR.."/shaders/love/pixel.glsl")
        if vertex_code and pixel_code then
            self.shader = love.graphics.newShader(pixel_code, vertex_code)
            -- Set the default brightness uniform.
            self.shader:send("brightness", 1.0)
        else
            error("Shader files not found.")
        end
    end
    return self
end

-- Expects a function that draws the scene.
function ShaderRenderer:render(drawFunction)
    if self.enabled and self.shader then
        love.graphics.setShader(self.shader)
        drawFunction()
        love.graphics.setShader()
    else
        drawFunction()
    end
end

function ShaderRenderer:toggle()
    self.enabled = not self.enabled
end

return ShaderRenderer
