-- Roblox Studio to Web Server Connector
-- Place this script in ServerScriptService in Roblox Studio

local HttpService = game:GetService("HttpService")

-- Configuration
local SERVER_URL = "https://your-api-domain.com/api" -- Replace with your web server URL
local API_KEY = "YOUR_SECRET_API_KEY"              -- Replace with your API key if applicable

local Connector = {}

--- Sends a GET request to the external server
-- @param endpoint string - e.g. "/stats" or "/get-data"
function Connector.getData(endpoint)
	local url = SERVER_URL .. endpoint
	local success, response = pcall(function()
		return HttpService:GetAsync(url, true, {
			["Authorization"] = "Bearer " .. API_KEY,
			["Accept"] = "application/json"
		})
	end)

	if success then
		print("[Roblox Connector] Data retrieved successfully:", response)
		local decodedData = HttpService:JSONDecode(response)
		return decodedData
	else
		warn("[Roblox Connector] Failed to fetch data:", response)
		return nil
	end
end

--- Sends a POST request to the external server
-- @param endpoint string - e.g. "/log-event" or "/save-player-data"
-- @param data table - Dictionary to send as JSON payload
function Connector.sendData(endpoint, data)
	local url = SERVER_URL .. endpoint
	local jsonPayload = HttpService:JSONEncode(data)

	local success, response = pcall(function()
		return HttpService:PostAsync(
			url,
			jsonPayload,
			Enum.HttpContentType.ApplicationJson,
			false,
			{
				["Authorization"] = "Bearer " .. API_KEY
			}
		)
	end)

	if success then
		print("[Roblox Connector] Data sent successfully:", response)
		return HttpService:JSONDecode(response)
	else
		warn("[Roblox Connector] Failed to send data:", response)
		return nil
	end
end

-- Example Usage on Game Start
local function onServerStart()
	print("[Roblox Connector] Testing connection to external server...")
	
	-- Test POST payload (e.g. sending server start notification)
	local payload = {
		placeId = game.PlaceId,
		jobId = game.JobId,
		timestamp = os.time(),
		event = "ServerStarted"
	}
	
	-- Connector.sendData("/server-status", payload)
end

onServerStart()

return Connector
