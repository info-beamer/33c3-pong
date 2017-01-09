local api, CHILDS, CONTENTS = ...

local W = 1920
local H = 1080
local PADDLE_SPEED = 0.5
local PADDLE_WIDTH = 220
local PADDLE_DEPTH = 20
local BALL_SIZE = 20
local BALL_X_SPEED = 5

local json = require "json"
local max, min, abs = math.max, math.min, math.abs

local running = false
local l, target_l
local r, target_r
local ball_x, ball_y, ball_speed, ball_vspeed
local score
local hiscore = 0
local num_players = 0

target_l = 50
target_r = 50

local pixel = resource.create_colored_texture(1,0,0, 0.6)
local font = resource.load_font(api.localized "font.ttf")
--

local remove_mapper = util.data_mapper{
    [api.localized "pos"] = function(data)
        local pkt = json.decode(data)
        target_l = pkt.l
        target_r = pkt.r
        num_players = pkt.num
    end;
}

local function restart(dir)
    ball_x = W / 2 -- - (W/4) * dir
    ball_y = H / 2
    ball_speed = BALL_X_SPEED  * dir
    ball_vspeed = 0
    l = target_l
    r = target_r
    score = 0
end

restart(-1)

local function p2y(percent) -- percent to y
    return H / 100 * percent
end

local function move_to(target, current)
    if current < target then
        return current + min(PADDLE_SPEED, target-current)
    else
        return current - min(PADDLE_SPEED, current-target)
    end
end

local function hit(paddle_y, paddle_speed)
   ball_speed = ball_speed * -1
   local off_center = (ball_y - paddle_y) / (PADDLE_WIDTH/2)
   ball_vspeed = ball_vspeed + off_center
   ball_vspeed = ball_vspeed + paddle_speed
   if r ~= 50 or l ~= 50 then
       score = score + 1
   end
   if score > hiscore then
       hiscore = score
   end
   print("HIT HIT", off_center)
end

local function step_game()
    l = move_to(target_l, l)
    r = move_to(target_r, r)
    ball_x = ball_x + ball_speed
    ball_y = ball_y + ball_vspeed

    if ball_y < 0 or ball_y > H then
        ball_vspeed = ball_vspeed * -1
    end

    if ball_speed < 0 then
        if ball_x < 0 then
            restart(1)
        end
        if ball_x - BALL_SIZE/2 < PADDLE_DEPTH then -- left
            local y = p2y(l)
            local target_y = p2y(target_l)
            if ball_y > y - PADDLE_WIDTH/2 - BALL_SIZE/2 and
               ball_y < y + PADDLE_WIDTH/2 + BALL_SIZE/2 then
               local moving = 0
               if y - 10 > target_y then
                   moving = 1
               elseif y + 10 < target_y then
                   moving = -1
               end
               hit(y, moving)
           end
        end
    end

    if ball_speed > 0 then
        if ball_x > W then
            restart(-1)
        end
        if ball_x + BALL_SIZE/2 > W - PADDLE_DEPTH then -- right
            local y = p2y(r)
            local target_y = p2y(target_r)
            if ball_y > y - PADDLE_WIDTH/2 - BALL_SIZE/2 and
               ball_y < y + PADDLE_WIDTH/2 + BALL_SIZE/2 then
               local moving = 0
               if y - 10 > target_y then
                   moving = 1
               elseif y + 10 < target_y then
                   moving = -1
               end
               hit(y, moving)
           end
        end
    end
end

local function draw_game()
    local y

    font:write(1420, 0, "33c3.infobeamer.com/pong", 30, 1,1,1,1)
    font:write(1420, 30, "score " .. score .. ", best " .. hiscore .. ", players " .. num_players, 30, 1,1,1,1)

    y = p2y(l)
    pixel:draw(0, y - PADDLE_WIDTH/2, PADDLE_DEPTH, y + PADDLE_WIDTH/2)

    -- gl.pushMatrix()
    -- gl.translate(5, y + PADDLE_WIDTH/2)
    -- gl.rotate(-90, 0, 0, 1)
    -- font:write(0, 0, "https://33c3.infobeamer.com/pong", PADDLE_DEPTH/1.5, 1,1,1,1)
    -- gl.popMatrix()

    y = p2y(r)
    pixel:draw(W-PADDLE_DEPTH, y - PADDLE_WIDTH/2, W, y + PADDLE_WIDTH/2)

    -- gl.pushMatrix()
    -- gl.translate(W-5, y - PADDLE_WIDTH/2)
    -- gl.rotate(90, 0, 0, 1)
    -- font:write(0, 0, "https://33c3.infobeamer.com/pong", PADDLE_DEPTH/1.5, 1,1,1,1)
    -- gl.popMatrix()

    pixel:draw(ball_x-BALL_SIZE/2, ball_y-BALL_SIZE/2,
               ball_x+BALL_SIZE/2, ball_y+BALL_SIZE/2)
end

local M = {}

function M.updated_config_json(config)
    running = false
    for idx = 1, #config.games do
        local game = config.games[idx]
        if game.serial == sys.get_env("SERIAL") then
            running = true
        end
    end
    print("RUNNING STATUS FOR PONG", running)
end

function M.task(starts, ends, custom)
    for now, x1, y1, x2, y2 in api.from_to(starts, ends) do
        if running then
            step_game()
            draw_game()
        end
    end
end

function M.unload()
    print "removing pong mapper"
    remove_mapper()
end

return M
