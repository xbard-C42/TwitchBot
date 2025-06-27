/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
import { GoogleGenAI } from "@google/genai";

// --- DOM Element References ---
// Status Bar
const botStatusIndicator = document.getElementById('bot-status-indicator') as HTMLElement;
const twitchStatusIndicator = document.getElementById('twitch-status-indicator') as HTMLElement;
const streamerbotStatusIndicator = document.getElementById('streamerbot-status-indicator') as HTMLElement;
const lnmStatusIndicator = document.getElementById('lnm-status-indicator') as HTMLElement;

// Bot Control
const toggleBotButton = document.getElementById('toggle-bot-button') as HTMLButtonElement;
const cycleMoodButton = document.getElementById('cycle-mood-button') as HTMLButtonElement;
const requestStatusReportButton = document.getElementById('request-status-report-button') as HTMLButtonElement;
const aiModelSelect = document.getElementById('ai-model-select') as HTMLSelectElement;
const aiMoodDisplay = document.getElementById('ai-mood') as HTMLElement;
const aiPersonalityDisplay = document.getElementById('ai-personality') as HTMLElement;
const moodLogOutput = document.getElementById('mood-log-output') as HTMLElement;
const aiFlightContextDisplay = document.getElementById('ai-flight-context') as HTMLElement;
const flightContextButtonsContainer = document.getElementById('flight-context-buttons') as HTMLElement;

// Voice Command Center
const toggleVoiceCommandsButton = document.getElementById('toggle-voice-commands-button') as HTMLButtonElement;
const voiceSystemStatusDisplay = document.getElementById('voice-system-status') as HTMLElement;
const vadStatusIndicator = document.getElementById('vad-status-indicator') as HTMLElement;
const voiceLogOutput = document.getElementById('voice-log-output') as HTMLElement;

// Voice System Details
const vdsSttEngine = document.getElementById('vds-stt-engine') as HTMLElement;
const vdsLanguage = document.getElementById('vds-language') as HTMLElement;
const vdsConfidence = document.getElementById('vds-confidence') as HTMLElement;
const vdsTimeout = document.getElementById('vds-timeout') as HTMLElement;
const vdsPhraseLimit = document.getElementById('vds-phrase-limit') as HTMLElement;
const vdsEnergyThreshold = document.getElementById('vds-energy-threshold') as HTMLElement;
const vdsDynamicEnergy = document.getElementById('vds-dynamic-energy') as HTMLElement;
const vdsPauseThreshold = document.getElementById('vds-pause-threshold') as HTMLElement;
const vdsPhraseThreshold = document.getElementById('vds-phrase-threshold') as HTMLElement;
const vdsVadAggressiveness = document.getElementById('vds-vad-aggressiveness') as HTMLElement;
const vdsMicSampleRate = document.getElementById('vds-mic-sample-rate') as HTMLElement;
const vdsMicChunkSize = document.getElementById('vds-mic-chunk-size') as HTMLElement;
const toggleTtsButton = document.getElementById('toggle-tts-button') as HTMLButtonElement;
const availableCommandsList = document.getElementById('available-commands-list') as HTMLElement;

// Flight Data
const fdCallsign = document.getElementById('fd-callsign') as HTMLElement;
const fdAircraft = document.getElementById('fd-aircraft') as HTMLElement;
const fdAltitude = document.getElementById('fd-altitude') as HTMLElement;
const fdSpeed = document.getElementById('fd-speed') as HTMLElement;
const fdHeading = document.getElementById('fd-heading') as HTMLElement;
const fdVspeed = document.getElementById('fd-vspeed') as HTMLElement;
const fdPhase = document.getElementById('fd-phase') as HTMLElement;
const fdNextWp = document.getElementById('fd-next-wp') as HTMLElement;
const fdEtaNext = document.getElementById('fd-eta-next') as HTMLElement;
const fdFuel = document.getElementById('fd-fuel') as HTMLElement;
const analyzeFuelButton = document.getElementById('analyze-fuel-button') as HTMLButtonElement;

// Flight & Automation Insights
const faMilestoneAltitudes = document.getElementById('fa-milestone-altitudes') as HTMLElement;
const faAutoSceneStatus = document.getElementById('fa-auto-scene-status') as HTMLElement;
const faWeatherInterval = document.getElementById('fa-weather-interval') as HTMLElement;
const flightMilestonesLog = document.getElementById('flight-milestones-log') as HTMLElement;

// System Health & Metrics
const metricsSystemStatus = document.getElementById('metrics-system-status') as HTMLElement;
const metricsVoiceQueue = document.getElementById('metrics-voice-queue') as HTMLElement;
const metricsLastVoiceCmd = document.getElementById('metrics-last-voice-cmd') as HTMLElement;
const metricsDbConnection = document.getElementById('metrics-db-connection') as HTMLElement;
const metricsSentryReporting = document.getElementById('metrics-sentry-reporting') as HTMLElement;

// Config Editor
const configEditorTextarea = document.getElementById('config-editor-textarea') as HTMLTextAreaElement;
const configEditorStatus = document.getElementById('config-editor-status') as HTMLElement;
const loadDefaultConfigButton = document.getElementById('load-default-config-button') as HTMLButtonElement;
const saveConfigButton = document.getElementById('save-config-button') as HTMLButtonElement;

// Diagnostics & Testing
const diagTestTwitchButton = document.getElementById('diag-test-twitch-button') as HTMLButtonElement;
const diagTestStreamerbotButton = document.getElementById('diag-test-streamerbot-button') as HTMLButtonElement;
const diagTestLnmButton = document.getElementById('diag-test-lnm-button') as HTMLButtonElement;
const diagTestOpenaiButton = document.getElementById('diag-test-openai-button') as HTMLButtonElement;
const diagTestTtsButton = document.getElementById('diag-test-tts-button') as HTMLButtonElement;
const diagVoiceIntentInput = document.getElementById('diag-voice-intent-input') as HTMLInputElement;
const diagClassifyIntentButton = document.getElementById('diag-classify-intent-button') as HTMLButtonElement;
const diagTriggerDecreeButton = document.getElementById('diag-trigger-decree-button') as HTMLButtonElement;
const diagTriggerMilestoneButton = document.getElementById('diag-trigger-milestone-button') as HTMLButtonElement;
const diagnosticsLogOutput = document.getElementById('diagnostics-log-output') as HTMLElement;

// Weather
const fetchWeatherButton = document.getElementById('fetch-weather-button') as HTMLButtonElement;
const weatherDisplay = document.getElementById('weather-display') as HTMLElement;

// Decrees & Loyalty
const issueDecreeButton = document.getElementById('issue-decree-button') as HTMLButtonElement;
const suggestDecreeButton = document.getElementById('suggest-decree-button') as HTMLButtonElement;
const decreeSuggestionsArea = document.getElementById('decree-suggestions-area') as HTMLElement;
const toggleSeasonalButton = document.getElementById('toggle-seasonal-button') as HTMLButtonElement;
const dlLoyaltyMultiplierInput = document.getElementById('dl-loyalty-multiplier-input') as HTMLInputElement;
const dlDecreeCooldownInput = document.getElementById('dl-decree-cooldown-input') as HTMLInputElement;
const saveAiSettingsButton = document.getElementById('save-ai-settings-button') as HTMLButtonElement;
const dlSeasonalStatus = document.getElementById('dl-seasonal-status') as HTMLElement;
const decreesList = document.getElementById('decrees-list') as HTMLElement;
const loyaltyList = document.getElementById('loyalty-list') as HTMLElement;

// User Loyalty Explorer
const loyaltySearchInput = document.getElementById('loyalty-search-input') as HTMLInputElement;
const loyaltyFindUserButton = document.getElementById('loyalty-find-user-button') as HTMLButtonElement;
const loyaltyUserNameDisplay = document.getElementById('loyalty-user-name') as HTMLElement;
const loyaltyUserScoreDisplay = document.getElementById('loyalty-user-score') as HTMLElement;
const loyaltyUserRankDisplay = document.getElementById('loyalty-user-rank') as HTMLElement;
const loyaltyUserLastInteractionDisplay = document.getElementById('loyalty-user-last-interaction') as HTMLElement;
const loyaltyAdjustScoreInput = document.getElementById('loyalty-adjust-score-input') as HTMLInputElement;
const loyaltyUpdateScoreButton = document.getElementById('loyalty-update-score-button') as HTMLButtonElement;
const loyaltyExplorerStatus = document.getElementById('loyalty-explorer-status') as HTMLElement;

// Stream Automation
const streamTitleInput = document.getElementById('stream-title-input') as HTMLInputElement;
const updateTitleButton = document.getElementById('update-title-button') as HTMLButtonElement;
const chatAnnouncementInput = document.getElementById('chat-announcement-input') as HTMLInputElement;
const sendAnnouncementButton = document.getElementById('send-announcement-button') as HTMLButtonElement;
const takeScreenshotButton = document.getElementById('take-screenshot-button') as HTMLButtonElement;
const sceneButtons = document.querySelectorAll('.scene-button');

// Airport Info Lookup
const icaoInput = document.getElementById('icao-input') as HTMLInputElement;
const lookupAirportButton = document.getElementById('lookup-airport-button') as HTMLButtonElement;
const airportInfoDisplay = document.getElementById('airport-info-display') as HTMLElement;

// Twitch Chat
const chatOutput = document.getElementById('chat-output') as HTMLElement;
const botChatInput = document.getElementById('bot-chat-input') as HTMLInputElement;
const sendBotMessageButton = document.getElementById('send-bot-message-button') as HTMLButtonElement;

// Quick Settings
const qsVoicePrefix = document.getElementById('qs-voice-prefix') as HTMLElement;
const qsVoiceActivation = document.getElementById('qs-voice-activation') as HTMLElement;
const qsAiPersonalityPrompt = document.getElementById('qs-ai-personality-prompt') as HTMLElement;
const qsAiModel = document.getElementById('qs-ai-model') as HTMLElement;
const qsLanguage = document.getElementById('qs-language') as HTMLElement;
const qsConfigFile = document.getElementById('qs-config-file') as HTMLElement;
const qsOpenAiApiKeyStatus = document.getElementById('qs-openai-api-key-status') as HTMLElement;
const qsAirportApiKeyStatus = document.getElementById('qs-airport-api-key-status') as HTMLElement;
const qsAzureSpeechKeyStatus = document.getElementById('qs-azure-speech-key-status') as HTMLElement;
const qsSentryStatus = document.getElementById('qs-sentry-status') as HTMLElement;
const qsVerboseLogging = document.getElementById('qs-verbose-logging') as HTMLElement;
const qsLogLevel = document.getElementById('qs-log-level') as HTMLElement;
const setLogLevelSelect = document.getElementById('set-log-level') as HTMLSelectElement;
const applyLogLevelButton = document.getElementById('apply-log-level-button') as HTMLButtonElement;
const logLevelStatus = document.getElementById('log-level-status') as HTMLElement;

// Gemini API
let ai: GoogleGenAI | null = null;
try {
    if (process.env.API_KEY) {
        ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    } else {
        console.warn("API_KEY environment variable not found. Gemini API features will be disabled.");
        if (diagTestOpenaiButton)
            diagTestOpenaiButton.title = "Gemini API Key not set in environment";
    }
}
catch (error) {
    console.error("Error initializing GoogleGenAI:", error);
    ai = null;
    if (diagTestOpenaiButton)
        diagTestOpenaiButton.title = "Error initializing Gemini API";
}


// --- State Variables ---
let isBotRunning = false;
let isVoiceEnabled = false;
let isTtsEnabled = false;
let isSeasonalContentActive = false;
const aiMoods = ["Analytical", "Dramatic", "Amused", "Impatient"];
let currentMoodIndex = 0;
let currentAiModel = "Gemini"; // Default AI Model
const voiceSystemStates = ["LISTENING", "PROCESSING", "EXECUTING", "COOLDOWN", "ERROR"];
let currentVoiceSystemStateIndex = 0;
const flightContexts = ["Ground", "Taxi", "Climb", "Cruise", "Descent", "Approach", "Landing"];
let currentFlightContextIndex = 0;
let currentLoyaltyUser: any = null;

const defaultConfigYaml = `personality:
  default_mood: "analytical"
  loyalty_multiplier: 1.5
  decree_cooldown: 300 # seconds

voice:
  activation_phrases:
    - "overlord"
    - "hey overlord"
    - "ai overlord"
  command_timeout: 5.0 # seconds for STT to wait for phrase
  phrase_limit: 10.0 # max duration of a voice command

flight_integration:
  milestone_announcements: true
  altitude_thresholds: [1000, 5000, 10000, 18000, 35000] # feet
  weather_update_interval: 300 # seconds
`;

// --- Helper Functions ---
function updateStatusIndicator(element: HTMLElement, isOnline: boolean, onlineText = "Online", offlineText = "Offline") {
    if (!element)
        return;
    element.textContent = isOnline ? onlineText : offlineText;
    element.className = isOnline ? 'status-online' : 'status-offline';
}

function updateVadStatusIndicator(isActive: boolean) {
    if (!vadStatusIndicator)
        return;
    vadStatusIndicator.textContent = isActive ? "Active" : "Inactive";
    vadStatusIndicator.className = isActive ? 'status-vad-active' : 'status-vad-inactive';
}

function appendToLog(logElement: HTMLElement, message: string, type = 'info') {
    if (!logElement)
        return;
    const placeholder = logElement.querySelector('.log-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    const logEntry = document.createElement('div');
    logEntry.classList.add('log-entry', `log-entry-${type}`);
    const timestamp = new Date().toLocaleTimeString();
    logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span> <span class="log-message">${message}</span>`;
    logElement.appendChild(logEntry);
    logElement.scrollTop = logElement.scrollHeight; // Auto-scroll
}

function appendToDiagnosticsLog(message: string, type = 'test-info') {
    if (!diagnosticsLogOutput)
        return;

    const placeholder = diagnosticsLogOutput.querySelector('.log-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    const logEntry = document.createElement('div');
    logEntry.classList.add('log-entry'); // General class
    if (type === 'test-success') {
        logEntry.classList.add('log-success');
    }
    else if (type === 'test-failure') {
        logEntry.classList.add('log-error');
    }
    else { // 'test-info'
        logEntry.classList.add('log-info');
    }
    const timestamp = new Date().toLocaleTimeString();
    logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span> <span class="log-message">${message}</span>`;
    diagnosticsLogOutput.appendChild(logEntry);
    diagnosticsLogOutput.scrollTop = diagnosticsLogOutput.scrollHeight;
}

function setPlaceholder(logElement: HTMLElement, text: string) {
    if (!logElement) return;
    
    // Check if it's a UL or DIV for decrees
    if (logElement.tagName === 'UL' || logElement.id === 'decree-suggestions-area') {
         logElement.innerHTML = `<li class="log-placeholder">${text}</li>`;
    } else {
        logElement.innerHTML = `<p class="log-placeholder">${text}</p>`;
    }
}


function setStatusMessage(element: HTMLElement, message: string, type = 'success', duration = 3000) {
    if (!element)
        return;
    element.textContent = message;
    element.className = `module-status-message ${type}`;
    if (duration > 0) {
        setTimeout(() => {
            element.textContent = '';
            element.className = 'module-status-message';
        }, duration);
    }
}

const sampleVoiceCommands = [
    {
        name: "Set Altitude",
        trigger: "overlord set altitude",
        desc: "Set autopilot altitude",
        aliases: "set altitude, altitude to",
        permissionLevel: "streamer",
        cooldown: "2.0s",
        expectedParameters: [{ name: "altitude", type: "number", description: "Target altitude in feet" }]
    },
    {
        name: "Set Heading",
        trigger: "overlord set heading",
        desc: "Set autopilot heading",
        aliases: "set heading, heading to, turn to",
        permissionLevel: "streamer",
        cooldown: "2.0s",
        expectedParameters: [{ name: "heading", type: "number (0-359)", description: "Target heading in degrees" }]
    },
    {
        name: "Contact ATC",
        trigger: "overlord contact tower",
        desc: "Display ATC contact information",
        aliases: "contact atc, call tower",
        permissionLevel: "viewer",
        cooldown: "5.0s",
        expectedParameters: [{ name: "facility", type: "text (e.g., tower, ground)", description: "Specific ATC facility" }]
    },
    { name: "Flight Status", trigger: "overlord flight status", desc: "Display detailed flight status", aliases: "status report, flight report", permissionLevel: "viewer", cooldown: "3.0s" },
    { name: "Weather Report", trigger: "overlord weather report", desc: "Display current weather", aliases: "weather, current weather", permissionLevel: "viewer", cooldown: "5.0s" },
    { name: "Emergency", trigger: "overlord emergency", desc: "Trigger emergency procedures", aliases: "", permissionLevel: "streamer", cooldown: "10.0s" },
    { name: "Screenshot", trigger: "overlord screenshot", desc: "Take and share screenshot", aliases: "take screenshot, capture screen", permissionLevel: "moderator", cooldown: "5.0s" },
    {
        name: "Change Scene",
        trigger: "overlord change scene",
        desc: "Change OBS scene",
        aliases: "switch scene, change view",
        permissionLevel: "streamer",
        cooldown: "1.0s",
        expectedParameters: [{ name: "scene_name", type: "text", description: "Name of the OBS scene" }]
    },
];

const sampleLoyaltyData: any = {
    "StreamViewer123": { name: "StreamViewer123", score: 1250, rank: "Digital Disciple", lastInteraction: new Date(Date.now() - 86400000 * 2).toLocaleDateString() },
    "AnotherFan": { name: "AnotherFan", score: 780, rank: "Acolyte", lastInteraction: new Date(Date.now() - 86400000 * 1).toLocaleDateString() },
    "LoyalFollowerX": { name: "LoyalFollowerX", score: 500, rank: "Initiate", lastInteraction: new Date().toLocaleDateString() },
    "NewbieUser": { name: "NewbieUser", score: 50, rank: "Drone", lastInteraction: new Date().toLocaleDateString() }
};

function getLoyaltyRank(score: number) {
    if (score >= 1000)
        return "Digital Disciple";
    if (score >= 750)
        return "Acolyte";
    if (score >= 500)
        return "Initiate";
    if (score >= 250)
        return "Follower";
    return "Drone";
}

function populateAvailableCommands() {
    if (!availableCommandsList)
        return;
    availableCommandsList.innerHTML = '';
    if (!isBotRunning) {
        setPlaceholder(availableCommandsList, 'Bot must be running to see commands.');
        return;
    }
    sampleVoiceCommands.forEach(cmd => {
        const li = document.createElement('li');
        let paramsHtml = '';
        if (cmd.expectedParameters && cmd.expectedParameters.length > 0) {
            paramsHtml += `<div class="command-parameters">Expected Parameters:<ul>`;
            cmd.expectedParameters.forEach(p => {
                paramsHtml += `<li><span class="parameter-name">${p.name}</span>: <span class="parameter-type">${p.type}</span>${p.description ? ` (${p.description})` : ''}</li>`;
            });
            paramsHtml += `</ul></div>`;
        }
        li.innerHTML = `
            <span class="command-trigger">${cmd.trigger}</span>
            <span class="command-description">${cmd.desc}</span>
            ${cmd.aliases ? `<span class="command-aliases">Aliases: ${cmd.aliases}</span>` : ''}
            <div class="command-details">
                <span class="command-detail-label">Permission:</span> <span class="command-detail-value">${cmd.permissionLevel}</span> | 
                <span class="command-detail-label">Cooldown:</span> <span class="command-detail-value">${cmd.cooldown}</span>
            </div>
            ${paramsHtml}
        `;
        availableCommandsList.appendChild(li);
    });
}

function updateAiPersonalityDisplay() {
    if (aiPersonalityDisplay) {
        let personalityText = `AI Overlord (${currentAiModel} Core`;
        if (currentAiModel !== "Gemini") {
            personalityText += " - Sim.";
        }
        personalityText += ")";
        aiPersonalityDisplay.textContent = personalityText;
    }
}


function updateSuggestDecreeButtonState() {
    if (suggestDecreeButton) {
        const isDisabled = !isBotRunning || currentAiModel !== "Gemini" || !ai;
        suggestDecreeButton.disabled = isDisabled;
        if (!ai) {
            suggestDecreeButton.title = "Gemini API Key not set. Cannot suggest decrees.";
        } else if (!isBotRunning) {
            suggestDecreeButton.title = "Bot must be running to suggest decrees.";
        } else if (currentAiModel !== "Gemini") {
            suggestDecreeButton.title = "Decree suggestions require the Gemini model.";
        } else {
            suggestDecreeButton.title = "Suggests decrees using the Gemini API";
        }
    }
}

// --- Event Handlers & Logic ---
// Bot Control
if (toggleBotButton) {
    toggleBotButton.addEventListener('click', () => {
        isBotRunning = !isBotRunning;
        updateStatusIndicator(botStatusIndicator, isBotRunning, "Running", "Stopped");
        toggleBotButton.textContent = isBotRunning ? "Stop Bot" : "Start Bot";
        if (aiModelSelect)
            aiModelSelect.disabled = isBotRunning; // Disable model selection while bot is running

        // Enable/disable controls based on bot state
        const controlsToToggle = [
            cycleMoodButton, requestStatusReportButton, toggleTtsButton,
            toggleSeasonalButton, saveAiSettingsButton, analyzeFuelButton,
            loyaltyFindUserButton, loyaltyUpdateScoreButton, applyLogLevelButton
            // suggestDecreeButton is handled by updateSuggestDecreeButtonState
        ];

        controlsToToggle.forEach(btn => {
            if (btn) {
                btn.disabled = !isBotRunning;
            }
        });
        
        document.querySelectorAll('.context-button').forEach(btn => (btn as HTMLButtonElement).disabled = !isBotRunning);
        
        updateSuggestDecreeButtonState();

        if (isBotRunning) {
            aiMoodDisplay.textContent = aiMoods[currentMoodIndex];
            updateAiPersonalityDisplay(); // Use new function
            currentFlightContextIndex = 0; // Reset to Ground
            if (aiFlightContextDisplay)
                aiFlightContextDisplay.textContent = flightContexts[currentFlightContextIndex];
            appendToLog(moodLogOutput, `Bot started. Initial mood: ${aiMoods[currentMoodIndex]}`, "mood");
            appendToLog(moodLogOutput, `Initial flight context: ${flightContexts[currentFlightContextIndex]}`, "mood");
            appendToLog(moodLogOutput, `Primary AI Model: ${currentAiModel}`, "system");

            setTimeout(() => populateSampleFlightData(), 1000);
            setTimeout(() => addSampleChatMessage("system", "AI Overlord Bot connected to chat."), 500);
            populateQuickSettings();
            populateVoiceDetails();
            populateFlightAutomationInsights();
            populateDecreeLoyaltyDetails();
            populateAvailableCommands();
            populateSystemHealthMetrics();
            appendToLog(flightMilestonesLog, "Flight system initialized.", "milestone");
            updateVadStatusIndicator(false);

        } else {
            if (aiMoodDisplay)
                aiMoodDisplay.textContent = "---";
            if (aiPersonalityDisplay)
                aiPersonalityDisplay.textContent = "---";
            if (aiFlightContextDisplay)
                aiFlightContextDisplay.textContent = "---";
            
            clearFlightData();
            clearQuickSettings();
            clearVoiceDetails();
            clearFlightAutomationInsights();
            clearDecreeLoyaltyDetails();
            clearSystemHealthMetrics();
            updateVadStatusIndicator(false);
            clearLoyaltyExplorer();

            setPlaceholder(voiceLogOutput, "Voice command activity will appear here...");
            setPlaceholder(chatOutput, "Twitch chat messages will appear here...");
            setPlaceholder(decreesList, "No decrees issued.");
            if (decreeSuggestionsArea) {
                setPlaceholder(decreeSuggestionsArea, "Decree ideas will appear here...");
                decreeSuggestionsArea.style.display = 'none';
            }
            setPlaceholder(moodLogOutput, "Mood changes will appear here...");
            setPlaceholder(flightMilestonesLog, "Flight milestones will appear here...");
            setPlaceholder(availableCommandsList, 'Bot must be running to see commands.');

            if (airportInfoDisplay)
                airportInfoDisplay.textContent = 'Airport data will appear here...';
            if (weatherDisplay)
                weatherDisplay.textContent = 'METAR data will appear here...';
            
            isVoiceEnabled = false;
            if(voiceSystemStatusDisplay)
                voiceSystemStatusDisplay.textContent = "Disabled";
            if(toggleVoiceCommandsButton)
                toggleVoiceCommandsButton.textContent = "Enable Voice";
            
            isTtsEnabled = false;
            if(toggleTtsButton)
                toggleTtsButton.textContent = "Enable TTS Output";
                
            isSeasonalContentActive = false;
            if(dlSeasonalStatus)
                dlSeasonalStatus.textContent = "Inactive";
            if(toggleSeasonalButton)
                toggleSeasonalButton.textContent = "Enable Seasonal";
                
             if(loyaltyUpdateScoreButton)
                loyaltyUpdateScoreButton.disabled = true; // Also disable if bot stops
        }
        
        updateStatusIndicator(twitchStatusIndicator, isBotRunning);
        updateStatusIndicator(streamerbotStatusIndicator, isBotRunning);
        updateStatusIndicator(lnmStatusIndicator, isBotRunning);
    });
}

if (aiModelSelect) {
    aiModelSelect.addEventListener('change', () => {
        currentAiModel = aiModelSelect.value;
        updateAiPersonalityDisplay();
        populateQuickSettings(); // Refresh quick settings to show new model
        updateSuggestDecreeButtonState();
        if (isBotRunning) {
            appendToLog(moodLogOutput, `Primary AI Model changed to: ${currentAiModel}`, "system");
        }
    });
}

if (cycleMoodButton) {
    cycleMoodButton.addEventListener('click', () => {
        if (!isBotRunning)
            return;
        currentMoodIndex = (currentMoodIndex + 1) % aiMoods.length;
        const newMood = aiMoods[currentMoodIndex];
        if (aiMoodDisplay)
            aiMoodDisplay.textContent = newMood;
        appendToLog(moodLogOutput, `Mood manually changed to: ${newMood}`, "mood");
    });
}

if (requestStatusReportButton) {
    requestStatusReportButton.addEventListener('click', () => {
        if (!isBotRunning)
            return;
        const reportParts = [
            "Simulated Full Status Report:",
            `- Bot Status: Running`,
            `- Primary AI Model: ${currentAiModel}`,
            `- AI Mood: ${aiMoodDisplay?.textContent || 'N/A'}`,
            `- AI Personality Prompt: ${qsAiPersonalityPrompt?.textContent?.substring(0, 50) || 'N/A'}...`,
            `- Flight Phase: ${fdPhase?.textContent || 'N/A'}`,
            `- Voice System: ${isVoiceEnabled ? (voiceSystemStatusDisplay?.textContent || 'Enabled') : "Disabled"}`,
            `- TTS Output: ${isTtsEnabled ? "Enabled" : "Disabled"}`,
            `- Log Level: ${qsLogLevel?.textContent || 'N/A'}`,
            `- OpenAI/Gemini Key: ${qsOpenAiApiKeyStatus?.textContent || 'N/A'}`,
            `- Airport API Key: ${qsAirportApiKeyStatus?.textContent || 'N/A'}`,
            `- Azure Speech Key: ${qsAzureSpeechKeyStatus?.textContent || 'N/A'}`,
            `- Sentry DSN: ${qsSentryStatus?.textContent || 'N/A'}`
        ];
        alert(reportParts.join("\n"));
        appendToLog(chatOutput, "AI Overlord: Generating full status report (simulated)...", "system");
    });
}


if (flightContextButtonsContainer) {
    flightContextButtonsContainer.addEventListener('click', (event) => {
        const target = event.target as HTMLElement;
        if (target.classList.contains('context-button')) {
             if (!isBotRunning)
                return;
            const context = target.dataset.context;
            if (context && aiFlightContextDisplay) {
                aiFlightContextDisplay.textContent = context;
                currentFlightContextIndex = flightContexts.indexOf(context);
                appendToLog(moodLogOutput, `Flight context influence changed to: ${context}`, "mood");
            }
        }
    });
}


// Voice Commands
if (toggleVoiceCommandsButton) {
    toggleVoiceCommandsButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to enable voice commands.");
            return;
        }
        isVoiceEnabled = !isVoiceEnabled;

        if (isVoiceEnabled) {
            currentVoiceSystemStateIndex = 0;
            if (voiceSystemStatusDisplay)
                voiceSystemStatusDisplay.textContent = voiceSystemStates[currentVoiceSystemStateIndex];
            appendToLog(voiceLogOutput, "Voice recognition system enabled.", "info");
            updateVadStatusIndicator(false); // Start as inactive
            
            // Simulate VAD activity and command processing
            setTimeout(() => {
                if (!isVoiceEnabled || !isBotRunning) return;
                updateVadStatusIndicator(true); // VAD detects speech
                appendToLog(voiceLogOutput, "VAD: Speech detected, recording...", "info");
            }, 1500);
            
            setTimeout(() => {
                if (!isVoiceEnabled || !isBotRunning) return;
                updateVadStatusIndicator(false); // VAD stops recording
                currentVoiceSystemStateIndex = (currentVoiceSystemStateIndex + 1) % voiceSystemStates.length; // Processing
                 if (voiceSystemStatusDisplay)
                    voiceSystemStatusDisplay.textContent = voiceSystemStates[currentVoiceSystemStateIndex];
                addSampleVoiceCommand("Hey Overlord, what's the flight status?", "GetFlightStatus", "Recognized");
                 if(metricsLastVoiceCmd)
                    metricsLastVoiceCmd.textContent = new Date().toLocaleTimeString();
                 if(metricsVoiceQueue)
                    metricsVoiceQueue.textContent = "1";
            }, 3000); // End of VAD active, start processing
            
            setTimeout(() => {
                if (!isVoiceEnabled || !isBotRunning) return;
                currentVoiceSystemStateIndex = (currentVoiceSystemStateIndex + 1) % voiceSystemStates.length; // Executing
                if (voiceSystemStatusDisplay)
                    voiceSystemStatusDisplay.textContent = voiceSystemStates[currentVoiceSystemStateIndex];
                if(metricsVoiceQueue)
                    metricsVoiceQueue.textContent = "0";
            }, 4500);
            
            setTimeout(() => {
                if (!isVoiceEnabled || !isBotRunning) return;
                currentVoiceSystemStateIndex = 0; // Back to Listening
                if (voiceSystemStatusDisplay)
                    voiceSystemStatusDisplay.textContent = voiceSystemStates[currentVoiceSystemStateIndex];
            }, 6000);

        } else {
            if (voiceSystemStatusDisplay)
                voiceSystemStatusDisplay.textContent = "Disabled";
            updateVadStatusIndicator(false);
            appendToLog(voiceLogOutput, "Voice recognition system disabled.", "info");
        }
        toggleVoiceCommandsButton.textContent = isVoiceEnabled ? "Disable Voice" : "Enable Voice";
    });
}

function addSampleVoiceCommand(rawText: string, intent: string, status: string) {
    const message = `Speech: "${rawText}" | Intent: ${intent} | Status: ${status}`;
    appendToLog(voiceLogOutput, message, "voice");
}

// Voice System Details
if (toggleTtsButton) {
    toggleTtsButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to toggle TTS.");
            return;
        }
        isTtsEnabled = !isTtsEnabled;
        toggleTtsButton.textContent = isTtsEnabled ? "Disable TTS Output" : "Enable TTS Output";
        alert(`TTS Output (simulated) ${isTtsEnabled ? "Enabled" : "Disabled"}`);
    });
}

function populateVoiceDetails() {
    if (!vdsSttEngine) return; // Ensure elements exist
    vdsSttEngine.textContent = "google";
    vdsLanguage.textContent = "en-US";
    vdsConfidence.textContent = "0.7";
    vdsTimeout.textContent = "5s";
    vdsPhraseLimit.textContent = "10s";
    vdsEnergyThreshold.textContent = "300";
    vdsDynamicEnergy.textContent = "True";
    vdsPauseThreshold.textContent = "0.8s";
    vdsPhraseThreshold.textContent = "0.3s";
    vdsVadAggressiveness.textContent = "Level 2";
    vdsMicSampleRate.textContent = "16000Hz";
    vdsMicChunkSize.textContent = "512 bytes";
}

function clearVoiceDetails() {
    const fields = [
        vdsSttEngine, vdsLanguage, vdsConfidence, vdsTimeout, vdsPhraseLimit,
        vdsEnergyThreshold, vdsDynamicEnergy, vdsPauseThreshold, vdsPhraseThreshold,
        vdsVadAggressiveness, vdsMicSampleRate, vdsMicChunkSize
    ];
    fields.forEach(field => { if (field) field.textContent = "---"; });
}


// Flight Data Simulation
function populateSampleFlightData() {
    if (!isBotRunning || !fdCallsign) return;
    fdCallsign.textContent = "AIO123";
    fdAircraft.textContent = "Boeing 737-800";
    fdAltitude.textContent = "35,000 ft";
    fdSpeed.textContent = "450 kts";
    fdHeading.textContent = "270°";
    fdVspeed.textContent = "+500 fpm";
    fdPhase.textContent = "Cruise";
    fdNextWp.textContent = "WAYP1";
    fdEtaNext.textContent = new Date(Date.now() + 15 * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    fdFuel.textContent = "75%";
    appendToLog(flightMilestonesLog, "Aircraft data loaded. Phase: Cruise.", "milestone");
    setTimeout(() => {
        if(!isBotRunning) return;
        appendToLog(flightMilestonesLog, "Milestone: Reached 35,000 ft", "milestone");
    }, 2000);
}

function clearFlightData() {
    if (!fdCallsign) return;
    fdCallsign.textContent = "N/A";
    fdAircraft.textContent = "N/A";
    fdAltitude.textContent = "0 ft";
    fdSpeed.textContent = "0 kts";
    fdHeading.textContent = "0°";
    fdVspeed.textContent = "0 fpm";
    fdPhase.textContent = "Grounded";
    fdNextWp.textContent = "---";
    fdEtaNext.textContent = "--:--";
    fdFuel.textContent = "100%";
}

if (analyzeFuelButton) {
    analyzeFuelButton.addEventListener('click', () => {
        if(!isBotRunning) return;
        appendToLog(flightMilestonesLog, "Fuel analysis initiated by streamer (simulated).", "milestone");
        alert("Simulated Fuel Analysis:\n- Current Fuel: " + (fdFuel?.textContent || 'N/A') + "\n- Estimated Endurance: 2h 30m\n- Recommendation: Sufficient for current flight plan.");
    });
}

// Flight Automation Insights
function populateFlightAutomationInsights() {
    if(!faMilestoneAltitudes) return;
    faMilestoneAltitudes.textContent = "1000, 5000, 10000, 18000, 35000 ft";
    faAutoSceneStatus.textContent = "Enabled (Rules Active)";
    faWeatherInterval.textContent = "300s";
}
function clearFlightAutomationInsights() {
    if(!faMilestoneAltitudes) return;
    faMilestoneAltitudes.textContent = "---";
    faAutoSceneStatus.textContent = "Disabled";
    faWeatherInterval.textContent = "---";
}

// System Health & Metrics
function populateSystemHealthMetrics() {
    if (!isBotRunning || !metricsSystemStatus) return;
    metricsSystemStatus.textContent = "All Systems Nominal";
    metricsVoiceQueue.textContent = "0";
    metricsLastVoiceCmd.textContent = "N/A";
    metricsDbConnection.textContent = "Connected";
    metricsSentryReporting.textContent = qsSentryStatus?.classList.contains('key-status-set') ? "Reporting Active" : "Inactive";
}
function clearSystemHealthMetrics() {
    if (!metricsSystemStatus) return;
    metricsSystemStatus.textContent = "---";
    metricsVoiceQueue.textContent = "---";
    metricsLastVoiceCmd.textContent = "---";
    metricsDbConnection.textContent = "---";
    metricsSentryReporting.textContent = "---";
}


// Config Editor Logic
if(loadDefaultConfigButton && configEditorTextarea) {
    loadDefaultConfigButton.addEventListener('click', () => {
        configEditorTextarea.value = defaultConfigYaml;
        setStatusMessage(configEditorStatus, "Default config loaded into editor.", 'info');
    });
}
if(saveConfigButton && configEditorTextarea) {
    saveConfigButton.addEventListener('click', () => {
        const currentConfig = configEditorTextarea.value;
        console.log("Simulated Save Config:", currentConfig);
        setStatusMessage(configEditorStatus, "Configuration saved (simulated).", 'success');
    });
}

// Diagnostics & Testing Logic
if(diagTestTwitchButton) {
    diagTestTwitchButton.addEventListener('click', () => {
        const success = Math.random() > 0.2; // Simulate success/failure
        if (success) {
            appendToDiagnosticsLog("Twitch API: Connection Test SUCCESSFUL. OAuth Token Valid. (Simulated)", 'test-success');
        } else {
            appendToDiagnosticsLog("Twitch API: Connection Test FAILED. Check OAuth Token or Network. (Simulated)", 'test-failure');
        }
    });
}
if(diagTestStreamerbotButton) {
    diagTestStreamerbotButton.addEventListener('click', () => {
         appendToDiagnosticsLog("Streamer.bot: WebSocket Connection Test SUCCESSFUL. (Simulated)", 'test-success');
    });
}
if(diagTestLnmButton) {
    diagTestLnmButton.addEventListener('click', () => {
        appendToDiagnosticsLog("LittleNavmap: Connection Test SUCCESSFUL. Flight data accessible. (Simulated)", 'test-success');
    });
}
if (diagTestOpenaiButton) {
    diagTestOpenaiButton.addEventListener('click', async () => {
        if (!ai) {
            appendToDiagnosticsLog("Gemini API: Test FAILED. API client not initialized (check API_KEY).", 'test-failure');
            return;
        }
        if (currentAiModel !== "Gemini") {
            appendToDiagnosticsLog(`Gemini API: Test SKIPPED. Current model is ${currentAiModel}. This test is for Gemini.`, 'test-info');
            return;
        }

        appendToDiagnosticsLog("Gemini API: Sending test query 'Echo: Hello Overlord'...", 'test-info');
        try {
            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash-preview-04-17',
                contents: 'Echo: Hello Overlord',
            });
            const textOutput = response.text;
            if (textOutput === null || textOutput === undefined) { // Check for undefined as well, as .text is string | undefined
                appendToDiagnosticsLog(`Gemini API: Test Query FAILED. Response text was null or undefined.`, 'test-failure');
            }
            else if (textOutput.includes("Hello Overlord")) {
                appendToDiagnosticsLog(`Gemini API: Test Query SUCCEEDED. Response: "${textOutput}"`, 'test-success');
            } else {
                appendToDiagnosticsLog(`Gemini API: Test Query UNEXPECTED RESPONSE. Response: "${textOutput}"`, 'test-failure');
            }
        } catch (e: any) {
            console.error("Gemini API test error:", e);
            appendToDiagnosticsLog(`Gemini API: Test Query FAILED. Error: ${e.message || e.toString()}`, 'test-failure');
        }
    });
}
if(diagTestTtsButton) {
    diagTestTtsButton.addEventListener('click', () => {
        appendToDiagnosticsLog("TTS Output: Synthesized test phrase 'Greetings Overlord' successfully. (Simulated)", 'test-info');
    });
}
if (diagClassifyIntentButton && diagVoiceIntentInput) {
    diagClassifyIntentButton.addEventListener('click', () => {
        const phrase = diagVoiceIntentInput.value.trim();
        if(!phrase) {
            appendToDiagnosticsLog("Voice Intent Test: Please enter a phrase to test.", 'test-info');
            return;
        }
        let intent = "UnknownIntent";
        let params = "{}";
        if (phrase.toLowerCase().includes("altitude")) {
            intent = "SetAltitude";
            const match = phrase.match(/\d+/);
            if(match)
                params = `{ altitude: ${match[0]} }`;
        } else if (phrase.toLowerCase().includes("weather")) {
            intent = "GetWeather";
        }
        appendToDiagnosticsLog(`Voice Intent Test: Input: "${phrase}" -> Intent: ${intent}, Params: ${params} (Simulated)`, 'test-info');
        diagVoiceIntentInput.value = "";
    });
}
if(diagTriggerDecreeButton) {
    diagTriggerDecreeButton.addEventListener('click', () => {
        appendToDiagnosticsLog("System Event: Test Decree triggered: 'All viewers must engage maximum hype!' (Simulated)", 'test-info');
        if(isBotRunning && decreesList)
            appendToLog(decreesList, `Test Decree: "All viewers must engage maximum hype!"`, "decree");
    });
}
if(diagTriggerMilestoneButton) {
    diagTriggerMilestoneButton.addEventListener('click', () => {
        appendToDiagnosticsLog("System Event: Test Flight Milestone triggered: 'Reached Test Waypoint ALPHA' (Simulated)", 'test-info');
        if(isBotRunning && flightMilestonesLog)
            appendToLog(flightMilestonesLog, "Test Milestone: Reached Test Waypoint ALPHA", "milestone");
    });
}

// Weather
if (fetchWeatherButton) {
    fetchWeatherButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to fetch weather.");
            return;
        }
        if (weatherDisplay)
            weatherDisplay.textContent = "Fetching weather...";
        setTimeout(() => {
            if (weatherDisplay)
                weatherDisplay.textContent = `METAR KLAX ${new Date().getDate()}2050Z 27010KT 10SM FEW030 SCT045 BKN060 25/15 A3001 RMK AO2 SLP160 T02500150`;
            appendToLog(chatOutput, "AI Overlord: Weather data updated for KLAX.", "chat");
        }, 1500);
    });
}

// Decrees & Loyalty
if (issueDecreeButton) {
    issueDecreeButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to issue decrees.");
            return;
        }
        const decreeText = prompt("Enter your decree, Overlord:", "All viewers must hydrate!");
        if (decreeText) {
            appendToLog(decreesList, `Manual Decree: "${decreeText}"`, "decree");
            appendToLog(chatOutput, `AI Overlord's Decree: ${decreeText}`, "chat");
        }
    });
}

async function handleSuggestDecrees() {
    if (!isBotRunning) {
        alert("Bot must be running to suggest decrees.");
        return;
    }
     if (currentAiModel !== "Gemini") {
        alert("Decree suggestions currently require the Gemini AI model to be active.");
        return;
    }
    if (!ai) {
        alert("Gemini API client not available. Cannot suggest decrees.");
        appendToDiagnosticsLog("Suggest Decrees: Gemini API client not initialized.", 'test-failure');
        return;
    }

    if(!decreeSuggestionsArea || !aiMoodDisplay || !aiFlightContextDisplay) return;

    const mood = aiMoodDisplay.textContent || "Analytical";
    const flightContext = aiFlightContextDisplay.textContent || "Cruise";
    const prompt = `You are an AI Overlord with a ${mood} mood, currently observing a flight in the ${flightContext} phase. Suggest 3 short, thematic decree ideas (max 15 words each) that I, the streamer, can issue to my viewers. Return as a JSON array of strings. Example: ["All drones must report fuel levels!", "Initiate protocol 'Maximum Hype'!", "Recalibrate your focus matrix."]`
    
    decreeSuggestionsArea.innerHTML = '<p class="log-placeholder">🔮 Conjuring decree ideas...</p>';
    decreeSuggestionsArea.style.display = 'block';
    
    if(suggestDecreeButton) suggestDecreeButton.disabled = true;

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash-preview-04-17',
            contents: prompt,
            config: { responseMimeType: "application/json" }
        });

        const responseText = response.text;
        if (responseText === null || responseText === undefined) {
            setPlaceholder(decreeSuggestionsArea, "Error: AI returned an empty response.");
            appendToDiagnosticsLog(`Suggest Decrees Error: AI returned a null or undefined text response.`, 'test-failure');
            updateSuggestDecreeButtonState();
            return;
        }
        
        let jsonStr = responseText.trim();
        const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
        const match = jsonStr.match(fenceRegex);
        if (match && match[2]) {
            jsonStr = match[2].trim();
        }

        const suggestions = JSON.parse(jsonStr);

        if (suggestions && suggestions.length > 0) {
            const ul = document.createElement('ul');
            suggestions.forEach((s: string) => {
                const li = document.createElement('li');
                li.textContent = s;
                li.onclick = () => {
                    const decreeText = prompt("Issue this decree?", s);
                    if (decreeText) {
                         appendToLog(decreesList, `AI Suggested Decree: "${decreeText}"`, "decree");
                         appendToLog(chatOutput, `AI Overlord's Decree: ${decreeText}`, "chat");
                    }
                };
                ul.appendChild(li);
            });
            decreeSuggestionsArea.innerHTML = '';
            decreeSuggestionsArea.appendChild(ul);
        } else {
            setPlaceholder(decreeSuggestionsArea, "No decree ideas found. Try again?");
        }
    } catch (error: any) {
        console.error("Error fetching decree suggestions:", error);
        setPlaceholder(decreeSuggestionsArea, `Error: ${error.message || "Could not fetch suggestions."}`);
        appendToDiagnosticsLog(`Suggest Decrees Error: ${error.message || error.toString()}`, 'test-failure');
    } finally {
        updateSuggestDecreeButtonState();
    }
}

if(suggestDecreeButton) {
    suggestDecreeButton.addEventListener('click', handleSuggestDecrees);
}


if (toggleSeasonalButton) {
    toggleSeasonalButton.addEventListener('click', () => {
        if (!isBotRunning) return;
        isSeasonalContentActive = !isSeasonalContentActive;
        if(dlSeasonalStatus)
            dlSeasonalStatus.textContent = isSeasonalContentActive ? "Active" : "Inactive";
        toggleSeasonalButton.textContent = isSeasonalContentActive ? "Disable Seasonal" : "Enable Seasonal";
        alert(`Seasonal Content (simulated) ${isSeasonalContentActive ? "Enabled" : "Disabled"}`);
    });
}
if (saveAiSettingsButton) {
    saveAiSettingsButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to save AI settings.");
            return;
        }
        const multiplier = dlLoyaltyMultiplierInput.value;
        const cooldown = dlDecreeCooldownInput.value;
        alert(`Simulated Save: Loyalty Multiplier set to ${multiplier}, Decree Cooldown to ${cooldown}s.`);
        appendToLog(moodLogOutput, `AI Settings (simulated) saved. Multiplier: ${multiplier}, Cooldown: ${cooldown}s.`, "system");
    });
}

function populateDecreeLoyaltyDetails(){
    if(!dlLoyaltyMultiplierInput) return;
    dlLoyaltyMultiplierInput.value = "1.5";
    dlDecreeCooldownInput.value = "300";
}

function clearDecreeLoyaltyDetails(){
    if(!dlLoyaltyMultiplierInput) return;
    dlLoyaltyMultiplierInput.value = "---";
    dlDecreeCooldownInput.value = "---";
    if(dlSeasonalStatus)
        dlSeasonalStatus.textContent = "Inactive";
}

// User Loyalty Explorer
if (loyaltyFindUserButton && loyaltySearchInput) {
    loyaltyFindUserButton.addEventListener('click', () => {
        if(!isBotRunning){
            setStatusMessage(loyaltyExplorerStatus, "Bot must be running to search users.", 'error');
            return;
        }
        const username = loyaltySearchInput.value.trim();
        if(!username){
             setStatusMessage(loyaltyExplorerStatus, "Please enter a username to search.", 'info');
             return;
        }
        
        const user = sampleLoyaltyData[username];
        if(user) {
            currentLoyaltyUser = user;
            if(loyaltyUserNameDisplay) loyaltyUserNameDisplay.textContent = user.name;
            if(loyaltyUserScoreDisplay) loyaltyUserScoreDisplay.textContent = user.score.toString();
            if(loyaltyUserRankDisplay) loyaltyUserRankDisplay.textContent = user.rank;
            if(loyaltyUserLastInteractionDisplay) loyaltyUserLastInteractionDisplay.textContent = user.lastInteraction;
            if(loyaltyUpdateScoreButton) loyaltyUpdateScoreButton.disabled = false;
            setStatusMessage(loyaltyExplorerStatus, `User '${username}' found.`, 'success');
        } else {
            clearLoyaltyExplorer(false); // Clear display but not input
            setStatusMessage(loyaltyExplorerStatus, `User '${username}' not found.`, 'error');
            currentLoyaltyUser = null;
        }
    });
}
if(loyaltyUpdateScoreButton && loyaltyAdjustScoreInput){
    loyaltyUpdateScoreButton.addEventListener('click', () => {
        if(!isBotRunning || !currentLoyaltyUser) {
             setStatusMessage(loyaltyExplorerStatus, "No user loaded or bot not running.", 'error');
            return;
        }
        const adjustmentText = loyaltyAdjustScoreInput.value.trim();
        const adjustment = parseInt(adjustmentText, 10);
        if(isNaN(adjustment)){
            setStatusMessage(loyaltyExplorerStatus, "Invalid score adjustment. Must be a number (e.g., +10 or -5).", 'error');
            return;
        }
        currentLoyaltyUser.score += adjustment;
        currentLoyaltyUser.rank = getLoyaltyRank(currentLoyaltyUser.score);
        currentLoyaltyUser.lastInteraction = new Date().toLocaleDateString();
        
        // Update display
        if(loyaltyUserScoreDisplay) loyaltyUserScoreDisplay.textContent = currentLoyaltyUser.score.toString();
        if(loyaltyUserRankDisplay) loyaltyUserRankDisplay.textContent = currentLoyaltyUser.rank;
        if(loyaltyUserLastInteractionDisplay) loyaltyUserLastInteractionDisplay.textContent = currentLoyaltyUser.lastInteraction;
        
        setStatusMessage(loyaltyExplorerStatus, `Updated ${currentLoyaltyUser.name}'s score by ${adjustment}. New score: ${currentLoyaltyUser.score}. New rank: ${currentLoyaltyUser.rank}.`, 'success');
        loyaltyAdjustScoreInput.value = ""; // Clear input
    });
}

function clearLoyaltyExplorer(clearSearchInput = true){
    if(clearSearchInput && loyaltySearchInput) loyaltySearchInput.value = "";
    if(loyaltyUserNameDisplay) loyaltyUserNameDisplay.textContent = "---";
    if(loyaltyUserScoreDisplay) loyaltyUserScoreDisplay.textContent = "---";
    if(loyaltyUserRankDisplay) loyaltyUserRankDisplay.textContent = "---";
    if(loyaltyUserLastInteractionDisplay) loyaltyUserLastInteractionDisplay.textContent = "---";
    if(loyaltyAdjustScoreInput) loyaltyAdjustScoreInput.value = "";
    if(loyaltyUpdateScoreButton) loyaltyUpdateScoreButton.disabled = true;
    if(loyaltyExplorerStatus) loyaltyExplorerStatus.textContent = "";
    currentLoyaltyUser = null;
}

// Stream Automation
if(updateTitleButton && streamTitleInput) {
    updateTitleButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to update title.");
            return;
        }
        const newTitle = streamTitleInput.value;
        if(newTitle) {
            alert(`Stream title (simulated) updated to: "${newTitle}"`);
            streamTitleInput.value = "";
            appendToLog(chatOutput, `AI Overlord: Stream title updated to "${newTitle}".`, "chat");
        } else {
            alert("Please enter a title.");
        }
    });
}
if(sendAnnouncementButton && chatAnnouncementInput) {
    sendAnnouncementButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to send announcements.");
            return;
        }
        const announcement = chatAnnouncementInput.value;
        if(announcement) {
            addSampleChatMessage("AI Overlord (Announcement)", announcement);
            chatAnnouncementInput.value = "";
        } else {
            alert("Please enter an announcement.");
        }
    });
}
if(takeScreenshotButton) {
    takeScreenshotButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to take screenshots.");
            return;
        }
        alert("Screenshot captured! (Simulated)");
        appendToLog(chatOutput, "AI Overlord: Screenshot captured and saved!", "chat");
    });
}

sceneButtons.forEach(button => {
    button.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to change scenes.");
            return;
        }
        const sceneName = (button as HTMLElement).dataset.sceneName;
        alert(`Switched to OBS Scene: ${sceneName} (Simulated)`);
        appendToLog(chatOutput, `AI Overlord: Switched to scene "${sceneName}".`, "chat");
    });
});


// Airport Info Lookup
if(lookupAirportButton && icaoInput) {
    lookupAirportButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot must be running to lookup airport info.");
            return;
        }
        const icao = icaoInput.value.trim().toUpperCase();
        if(icao && icao.length >= 3 && icao.length <= 4) {
            if(airportInfoDisplay) airportInfoDisplay.textContent = `Fetching info for ${icao}...`;
            setTimeout(() => {
                if(!isBotRunning) return; // check again in case bot stopped
                if(airportInfoDisplay)
                    airportInfoDisplay.textContent = `Simulated Data for ${icao}:\nName: ${icao} International Airport\nLocation: City, Country\nMETAR: ${icao} 101250Z 27010KT 9999 SCT030 25/15 Q1012`;
            }, 1500);
        } else {
            alert("Please enter a valid 3 or 4 letter ICAO code.");
        }
    });
}

// Twitch Chat
function addSampleChatMessage(user: string, message: string) {
    const formattedMessage = `<strong>${user}:</strong> ${message}`;
    appendToLog(chatOutput, formattedMessage, "chat");
}
if (sendBotMessageButton && botChatInput) {
    sendBotMessageButton.addEventListener('click', () => {
        if (!isBotRunning) {
            alert("Bot needs to be running to send messages.");
            return;
        }
        const message = botChatInput.value.trim();
        if (message) {
            addSampleChatMessage("AI Overlord (Manual)", message);
            botChatInput.value = '';
        }
    });
    botChatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            if (sendBotMessageButton)
                sendBotMessageButton.click();
        }
    });
}

// Quick Settings
function updateKeyStatusDisplay(element: HTMLElement, isSet: boolean, isCritical = true) {
    if (!element) return;
    element.classList.remove('key-status-set', 'key-status-not-set', 'key-status-optional-not-set');
    if (isSet) {
        element.textContent = "✓ Set";
        element.classList.add('key-status-set');
    } else {
        if (isCritical) {
            element.textContent = "⚠️ Not Set";
            element.classList.add('key-status-not-set');
        } else {
            element.textContent = "Not Set";
            element.classList.add('key-status-optional-not-set');
        }
    }
}


function populateQuickSettings() {
    if(!qsVoicePrefix) return;
    qsVoicePrefix.textContent = "Hey Overlord";
    qsVoiceActivation.textContent = "hey Overlord, assistant, overlord";
    qsAiPersonalityPrompt.textContent = "You are an AI Overlord managing a flight simulation Twitch channel. You are sometimes dramatic, sometimes analytical, but always in command.";

    // Update AI Model display in Quick Settings
    if (qsAiModel) {
        let modelText = currentAiModel;
        if(currentAiModel === "Gemini") modelText += " (Active)";
        else modelText += " (Simulated)";
        qsAiModel.textContent = modelText;
    }

    qsLanguage.textContent = "en-US";
    if(qsConfigFile) qsConfigFile.textContent = "config.yaml";
    
    // Simulate API key statuses
    const openAiSet = !!ai; // True if 'ai' (Gemini client) is initialized
    const airportApiSet = false; // Simulate as not set
    const azureSpeechSet = true; // Simulate as set
    const sentrySet = false; // Simulate as not set (optional)

    updateKeyStatusDisplay(qsOpenAiApiKeyStatus, openAiSet, true);
    updateKeyStatusDisplay(qsAirportApiKeyStatus, airportApiSet, true);
    updateKeyStatusDisplay(qsAzureSpeechKeyStatus, azureSpeechSet, true);
    updateKeyStatusDisplay(qsSentryStatus, sentrySet, false);

    qsVerboseLogging.textContent = "False";
    const currentLogLevel = "INFO"; // Default or from .env
    qsLogLevel.textContent = currentLogLevel;
    if(setLogLevelSelect) setLogLevelSelect.value = currentLogLevel;
}

function clearQuickSettings() {
    const textFieldsToReset = [
        qsVoicePrefix, qsVoiceActivation, qsAiPersonalityPrompt, qsAiModel,
        qsLanguage, qsConfigFile, qsVerboseLogging, qsLogLevel
    ];
    textFieldsToReset.forEach(field => {
        if (field) {
            field.textContent = "---";
        }
    });

    // Use updateKeyStatusDisplay for API key statuses to show "Not Set" state
    if(qsOpenAiApiKeyStatus) updateKeyStatusDisplay(qsOpenAiApiKeyStatus, false, true);
    if(qsAirportApiKeyStatus) updateKeyStatusDisplay(qsAirportApiKeyStatus, false, true);
    if(qsAzureSpeechKeyStatus) updateKeyStatusDisplay(qsAzureSpeechKeyStatus, false, true);
    if(qsSentryStatus) updateKeyStatusDisplay(qsSentryStatus, false, false);
    
    if(setLogLevelSelect) setLogLevelSelect.value = "INFO";
    if(logLevelStatus) logLevelStatus.textContent = "";

}

if(applyLogLevelButton && setLogLevelSelect && qsLogLevel && logLevelStatus) {
    applyLogLevelButton.addEventListener('click', () => {
        if (!isBotRunning) {
             setStatusMessage(logLevelStatus, "Bot must be running to change log level.", 'error');
             return;
        }
        const newLevel = setLogLevelSelect.value;
        qsLogLevel.textContent = newLevel;
        setStatusMessage(logLevelStatus, `Log level set to ${newLevel} (Simulated).`, 'success');
    });
}


// Initial Setup
function initializeDashboard() {
    updateStatusIndicator(botStatusIndicator, false, "Running", "Stopped");
    updateStatusIndicator(twitchStatusIndicator, false);
    updateStatusIndicator(streamerbotStatusIndicator, false);
    updateStatusIndicator(lnmStatusIndicator, false);

    if (voiceSystemStatusDisplay)
        voiceSystemStatusDisplay.textContent = "Disabled";
    updateVadStatusIndicator(false);
    if (aiMoodDisplay)
        aiMoodDisplay.textContent = "---";
        
    // Set initial AI Model and Personality Display
    if (aiModelSelect) {
        aiModelSelect.value = currentAiModel;
        aiModelSelect.disabled = false; // Enable model selection when bot is stopped
    }
    updateAiPersonalityDisplay();

    if (aiFlightContextDisplay)
        aiFlightContextDisplay.textContent = "---";

    const initialDisableControls = [
        cycleMoodButton, requestStatusReportButton, toggleTtsButton,
        toggleSeasonalButton, saveAiSettingsButton, analyzeFuelButton,
        loyaltyFindUserButton, loyaltyUpdateScoreButton, applyLogLevelButton
    ];
    initialDisableControls.forEach(btn => { if(btn) btn.disabled = true; });
    
    updateSuggestDecreeButtonState(); // Centralized update
    document.querySelectorAll('.context-button').forEach(btn => (btn as HTMLButtonElement).disabled = true);
    
    clearQuickSettings(); // Clears and sets API keys to "Not Set" via updateKeyStatusDisplay
    clearVoiceDetails();
    clearFlightAutomationInsights();
    clearDecreeLoyaltyDetails();
    clearSystemHealthMetrics();
    clearLoyaltyExplorer();

    setPlaceholder(voiceLogOutput, "Voice command activity will appear here...");
    setPlaceholder(chatOutput, "Twitch chat messages will appear here...");
    setPlaceholder(decreesList, "No decrees issued.");
    if(decreeSuggestionsArea) {
        setPlaceholder(decreeSuggestionsArea, "Decree ideas will appear here...");
        decreeSuggestionsArea.style.display = 'none';
    }
    setPlaceholder(moodLogOutput, "Mood changes will appear here...");
    setPlaceholder(flightMilestonesLog, "Flight milestones will appear here...");
    setPlaceholder(availableCommandsList, 'No commands loaded.');
    if (airportInfoDisplay)
        airportInfoDisplay.textContent = 'Airport data will appear here...';
    if (weatherDisplay)
        weatherDisplay.textContent = 'METAR data will appear here...';
    setPlaceholder(diagnosticsLogOutput, "Diagnostic test results will appear here...");

    if (configEditorTextarea)
        configEditorTextarea.value = defaultConfigYaml;
    if (configEditorStatus)
        configEditorStatus.textContent = "";
    if (loyaltyExplorerStatus)
        loyaltyExplorerStatus.textContent = "";
    if (logLevelStatus)
        logLevelStatus.textContent = "";

    setTimeout(() => {
        if (!isBotRunning && chatOutput)
            addSampleChatMessage("StreamViewer123", "Hello Overlord! Great stream!");
    }, 2000);
    setTimeout(() => {
        if (!isBotRunning && chatOutput)
            addSampleChatMessage("AnotherFan", "!status");
    }, 4000);

    // Populate quick settings on initial load as well to reflect default AI model and API key status
    populateQuickSettings();
    updateSuggestDecreeButtonState(); // Ensure button state is correct on init
}

// --- Main ---
document.addEventListener('DOMContentLoaded', initializeDashboard);