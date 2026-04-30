const healthStatus = document.querySelector("#health-status");
const siteLanguageSelect = document.querySelector("#site-language-select");
const navButtons = document.querySelectorAll("[data-screen-target]");
const screens = document.querySelectorAll(".screen");
const modeButtons = document.querySelectorAll("[data-mode-target]");
const modePanels = document.querySelectorAll(".input-panel");
const uploadForm = document.querySelector("#upload-form");
const audioFileInput = document.querySelector("#audio-file");
const uploadButton = document.querySelector("#upload-button");
const recordStartButton = document.querySelector("#record-start");
const recordStopButton = document.querySelector("#record-stop");
const recordUploadButton = document.querySelector("#record-upload");
const recordStatusEl = document.querySelector("#record-status");
const recordPreview = document.querySelector("#record-preview");
const micSelect = document.querySelector("#mic-select");
const settingsMicSelect = document.querySelector("#settings-mic-select");
const languageSelect = document.querySelector("#language-select");
const settingsLanguageSelect = document.querySelector("#settings-language-select");
const refreshMicsButton = document.querySelector("#refresh-mics");
const requestMicAccessButton = document.querySelector("#request-mic-access");
const micHelpEl = document.querySelector("#mic-help");
const liveTranscriptEl = document.querySelector("#live-transcript");
const liveSubtitleEl = document.querySelector("#live-subtitle");
const speechStatusEl = document.querySelector("#speech-status");
const micMeterEl = document.querySelector("#mic-meter");
const recordingDotEl = document.querySelector("#recording-dot");
const taskIdEl = document.querySelector("#task-id");
const taskStatusEl = document.querySelector("#task-status");
const taskProgressEl = document.querySelector("#task-progress");
const taskDurationEl = document.querySelector("#task-duration");
const taskSpeakersEl = document.querySelector("#task-speakers");
const taskMessageEl = document.querySelector("#task-message");
const taskErrorEl = document.querySelector("#task-error");
const progressBar = document.querySelector("#progress-bar");
const detectedLanguageEl = document.querySelector("#detected-language");
const transcriptPreviewEl = document.querySelector("#transcript-preview");
const speakerPreviewEl = document.querySelector("#speaker-preview");
const translationPreviewEl = document.querySelector("#translation-preview");
const detailedSummaryPreviewEl = document.querySelector("#detailed-summary-preview");
const summaryPreviewEl = document.querySelector("#summary-preview");
const downloadLinksEl = document.querySelector("#download-links");

let pollTimer = null;
let mediaRecorder = null;
let recordedChunks = [];
let recordedBlob = null;
let recordingStream = null;
let speechRecognition = null;
let speechFinalText = "";
let audioContext = null;
let analyser = null;
let meterSource = null;
let meterFrame = null;
let meterData = null;
let autoUploadAfterStop = false;

const MIC_STORAGE_KEY = "qazscribe.selectedMicrophoneId";
const MIC_PERMISSION_STORAGE_KEY = "qazscribe.microphonePermissionGranted";
const LANGUAGE_STORAGE_KEY = "qazscribe.speechLanguage";
const SITE_LANGUAGE_STORAGE_KEY = "qazscribe.siteLanguage";

const siteLanguages = [
  { code: "ru", label: "Рус" },
  { code: "kk", label: "Қаз" },
  { code: "en", label: "Eng" },
];

const speechLanguages = [
  { code: "auto", labelKey: "speechAuto" },
  { code: "ru-RU", label: "Русский" },
  { code: "kk-KZ", label: "Қазақша" },
  { code: "ky-KG", label: "Кыргызча" },
  { code: "uz-UZ", label: "O'zbekcha" },
  { code: "tt-RU", label: "Татарча" },
  { code: "tg-TJ", label: "Тоҷикӣ" },
  { code: "az-AZ", label: "Azərbaycanca" },
  { code: "tk-TM", label: "Türkmençe" },
  { code: "be-BY", label: "Беларуская" },
  { code: "uk-UA", label: "Українська" },
];

const translations = {
  ru: {
    siteLanguage: "Язык сайта",
    brandSubtitle: "Протоколы конференций и заседаний",
    navWelcome: "Главная",
    navCapture: "Запись",
    navResults: "Результат",
    navSettings: "Настройки",
    healthChecking: "Проверяю сервер...",
    healthOk: "Сервер работает",
    healthOffline: "Сервер недоступен",
    heroEyebrow: "Локальная транскрибация для деловых задач",
    heroTitle: "Запишите речь или загрузите аудио",
    heroCopy:
      "QazScribe помогает получить текст, казахскую версию, краткую структуру и документы для экспорта. Сначала проверьте микрофон, затем отправьте запись на обработку.",
    heroLanguages:
      "Русский, казахский, кыргызский, узбекский, татарский, таджикский, азербайджанский, туркменский, белорусский и украинский.",
    startWork: "Начать работу",
    chooseMic: "Выбрать микрофон",
    ready: "Готово к тесту",
    micOrFile: "Микрофон или файл",
    heroStatusCopy: "После обработки появятся текст, резюме и ссылки на документы.",
    step1Title: "Начните запись с микрофона",
    step1Copy: "Нажмите кнопку микрофона. Разрешите браузеру доступ к микрофону при запросе.",
    step2Title: "Говорите чётко",
    step2Copy:
      "Черновой текст может появляться в браузере в реальном времени. Команды «точка», «запятая», «новый абзац» помогают оформить пунктуацию.",
    step3Title: "Или загрузите аудиофайл",
    step3Copy:
      "Переключитесь в режим «Файл» и загрузите MP3, WAV, M4A, OGG, WEBM или MP4. Модель обработает запись на вашем сервере.",
    step4Title: "Отредактируйте и экспортируйте",
    step4Copy: "Проверьте текст, внесите правки, затем скачайте TXT, SRT, VTT, JSON, PDF, DOCX или HTML.",
    sourceSpeech: "Источник речи",
    recordOrFile: "Запись или файл",
    mic: "Микрофон",
    file: "Файл",
    micMode: "Режим микрофона",
    recordHere: "Записать речь здесь",
    browserRecord: "браузерная запись",
    speechLanguage: "Язык речи",
    refreshMics: "Обновить список",
    livePrompt: "Нажмите «Начать запись», затем говорите рядом с микрофоном.",
    startRecording: "Начать запись",
    stopAndProcess: "Остановить и обработать",
    uploadRecording: "Отправить запись",
    recordNotStarted: "Запись ещё не начата.",
    liveDraft: "Черновой текст в браузере",
    waiting: "ожидание",
    liveTranscriptPlaceholder:
      "Если браузер поддерживает распознавание речи, черновой текст появится здесь во время записи.",
    fileMode: "Режим файла",
    uploadReadyFile: "Загрузить готовую запись",
    fileLabel: "Аудиофайл или видеофайл с речью",
    sendToProcessing: "Отправить на обработку",
    supportedFiles: "Поддерживаются: mp3, wav, m4a, ogg, webm, mp4.",
    state: "Состояние",
    serverAndTask: "Сервер и задача",
    openResult: "Открыть результат",
    taskInitial: "Загрузите файл или запись, чтобы создать задачу.",
    processing: "Обработка",
    result: "Результат",
    taskDetails: "Детали обработки",
    taskId: "Номер задачи",
    stage: "Этап",
    progress: "Готовность",
    duration: "Длительность",
    speakers: "Спикеры",
    transcript: "Распознанный текст",
    detectedLanguage: "Определённый язык",
    speakerTranscript: "Полная расшифровка по спикерам",
    kazakhVersion: "Казахская версия",
    fullNotes: "Основной полный конспект",
    shortSummary: "Краткое резюме",
    downloads: "Скачать результат",
    settings: "Настройки",
    micAndMode: "Микрофон и режим обработки",
    input: "Ввод",
    micChoice: "Выбор микрофона",
    allowAccess: "Разрешить доступ",
    activeMic: "Активный микрофон",
    draftLanguage: "Язык черновых субтитров",
    micHelp: "Если нужный микрофон не отображается, нажмите «Разрешить доступ», затем обновите список.",
    currentMode: "Текущий режим",
    recognition: "Распознавание",
    recognitionValue: "Whisper и Hugging Face ASR на backend",
    cisLanguages: "Языки СНГ",
    workMode: "Режим работы",
    workModeValue: "Локальная обработка на сервере организации",
    export: "Экспорт",
    speechAuto: "Авто (язык устройства)",
    noDocs: "Документы появятся после завершения обработки.",
    noTask: "Пока нет",
    taskWaiting: "Ожидание",
    transcriptFallback: "Текст появится после обработки модели.",
    translationFallback: "Перевод появится после обработки.",
    speakersFallback: "Спикеры появятся после обработки.",
    notesFallback: "Конспект появится после обработки.",
    summaryFallback: "Краткое резюме появится после обработки.",
    statusQueued: "В очереди",
    statusProcessing: "Обработка",
    statusConverting: "Конвертация аудио",
    statusTranscribing: "Распознавание речи",
    statusTranslating: "Перевод",
    statusSummarizing: "Резюме",
    statusDocuments: "Подготовка документов",
    statusCompleted: "Готово",
    statusFailed: "Ошибка",
    msgQueued: "Файл принят. Задача ожидает обработки.",
    msgConverting: "Приводим аудио к формату mono 16 kHz WAV.",
    msgTranscribing: "Модель распознаёт речь.",
    msgTranslating: "Готовим казахскую версию текста.",
    msgSummarizing: "Собираем краткое резюме и структуру.",
    msgDocuments: "Формируем документы.",
    msgCompleted: "Готово. Документы можно скачать ниже.",
    msgFailed: "Обработка остановилась с ошибкой.",
    uploadFailed: "Загрузка не прошла.",
    chooseFileFirst: "Сначала выберите аудио или видеофайл.",
    subtitleIdle: "Субтитры появятся здесь во время речи.",
    speakNow: "Говорите. Если браузер поддерживает распознавание, текст появится здесь.",
    recordReady: "Запись готова к загрузке.",
    recordingNow: "Идёт запись. Говорите в выбранный микрофон.",
    recordFirst: "Сначала запишите аудио.",
    sendingRecord: "Запись отправляется на сервер. После обработки появится резюме.",
    recordUploaded: "Запись загружена. Можно записать заново или отправить ещё раз.",
    micAccessFailed: "Не удалось получить доступ к микрофону.",
    stoppingRecord: "Останавливаю запись и готовлю обработку...",
    uploadingRecord: "Загружаю запись...",
    uploadingMicRecord: "Загружаю запись с микрофона...",
    browserUnsupported: "Браузер не поддерживает запись с микрофона.",
  },
  kk: {
    siteLanguage: "Сайт тілі",
    brandSubtitle: "Конференциялар мен отырыстар хаттамалары",
    navWelcome: "Басты",
    navCapture: "Жазу",
    navResults: "Нәтиже",
    navSettings: "Баптау",
    healthChecking: "Сервер тексерілуде...",
    healthOk: "Сервер жұмыс істеп тұр",
    healthOffline: "Сервер қолжетімсіз",
    heroEyebrow: "Іскерлік міндеттерге арналған жергілікті транскрибация",
    heroTitle: "Сөзді жазыңыз немесе аудио жүктеңіз",
    heroCopy:
      "QazScribe мәтін, қазақша нұсқа, қысқа құрылым және экспорт құжаттарын дайындайды. Алдымен микрофонды тексеріп, жазбаны өңдеуге жіберіңіз.",
    heroLanguages:
      "Орыс, қазақ, қырғыз, өзбек, татар, тәжік, әзербайжан, түрікмен, беларус және украин тілдері.",
    startWork: "Жұмысты бастау",
    chooseMic: "Микрофон таңдау",
    ready: "Тестке дайын",
    micOrFile: "Микрофон немесе файл",
    heroStatusCopy: "Өңдеуден кейін мәтін, түйіндеме және құжат сілтемелері пайда болады.",
    step1Title: "Микрофоннан жазуды бастаңыз",
    step1Copy: "Микрофон батырмасын басыңыз. Браузер сұраса, микрофонға рұқсат беріңіз.",
    step2Title: "Анық сөйлеңіз",
    step2Copy:
      "Черновик мәтін браузерде нақты уақытта көрінуі мүмкін. «нүкте», «үтір», «жаңа абзац» командалары пунктуацияға көмектеседі.",
    step3Title: "Немесе аудиофайл жүктеңіз",
    step3Copy:
      "«Файл» режиміне өтіп, MP3, WAV, M4A, OGG, WEBM немесе MP4 жүктеңіз. Модель жазбаны серверде өңдейді.",
    step4Title: "Тексеріп, экспорттаңыз",
    step4Copy: "Мәтінді тексеріп, түзетіңіз, кейін TXT, SRT, VTT, JSON, PDF, DOCX немесе HTML жүктеңіз.",
    sourceSpeech: "Сөйлеу көзі",
    recordOrFile: "Жазу немесе файл",
    mic: "Микрофон",
    file: "Файл",
    micMode: "Микрофон режимі",
    recordHere: "Сөйлеуді осы жерде жазыңыз",
    browserRecord: "браузерлік жазба",
    speechLanguage: "Сөйлеу тілі",
    refreshMics: "Тізімді жаңарту",
    livePrompt: "«Жазуды бастау» батырмасын басып, микрофонға жақын сөйлеңіз.",
    startRecording: "Жазуды бастау",
    stopAndProcess: "Тоқтату және өңдеу",
    uploadRecording: "Жазбаны жіберу",
    recordNotStarted: "Жазу әлі басталған жоқ.",
    liveDraft: "Браузердегі черновик мәтін",
    waiting: "күту",
    liveTranscriptPlaceholder:
      "Егер браузер сөйлеуді тануды қолдаса, жазу кезінде черновик мәтін осы жерде пайда болады.",
    fileMode: "Файл режимі",
    uploadReadyFile: "Дайын жазбаны жүктеу",
    fileLabel: "Сөзі бар аудио немесе видеофайл",
    sendToProcessing: "Өңдеуге жіберу",
    supportedFiles: "Қолдау көрсетіледі: mp3, wav, m4a, ogg, webm, mp4.",
    state: "Күйі",
    serverAndTask: "Сервер және тапсырма",
    openResult: "Нәтижені ашу",
    taskInitial: "Тапсырма жасау үшін файл немесе жазба жүктеңіз.",
    processing: "Өңдеу",
    result: "Нәтиже",
    taskDetails: "Өңдеу мәліметтері",
    taskId: "Тапсырма нөмірі",
    stage: "Кезең",
    progress: "Дайындық",
    duration: "Ұзақтығы",
    speakers: "Спикерлер",
    transcript: "Танылған мәтін",
    detectedLanguage: "Анықталған тіл",
    speakerTranscript: "Спикерлер бойынша толық мәтін",
    kazakhVersion: "Қазақша нұсқа",
    fullNotes: "Негізгі толық конспект",
    shortSummary: "Қысқа түйіндеме",
    downloads: "Нәтижені жүктеу",
    settings: "Баптау",
    micAndMode: "Микрофон және өңдеу режимі",
    input: "Кіріс",
    micChoice: "Микрофон таңдау",
    allowAccess: "Рұқсат беру",
    activeMic: "Белсенді микрофон",
    draftLanguage: "Черновик субтитр тілі",
    micHelp: "Қажетті микрофон көрінбесе, «Рұқсат беру» басып, тізімді жаңартыңыз.",
    currentMode: "Ағымдағы режим",
    recognition: "Тану",
    recognitionValue: "Backend-тағы Whisper және Hugging Face ASR",
    cisLanguages: "ТМД тілдері",
    workMode: "Жұмыс режимі",
    workModeValue: "Ұйым серверінде жергілікті өңдеу",
    export: "Экспорт",
    speechAuto: "Авто (құрылғы тілі)",
    noDocs: "Құжаттар өңдеу аяқталғаннан кейін пайда болады.",
    noTask: "Әзірге жоқ",
    taskWaiting: "Күту",
    transcriptFallback: "Мәтін модель өңдегеннен кейін пайда болады.",
    translationFallback: "Аударма өңдеуден кейін пайда болады.",
    speakersFallback: "Спикерлер өңдеуден кейін пайда болады.",
    notesFallback: "Конспект өңдеуден кейін пайда болады.",
    summaryFallback: "Қысқа түйіндеме өңдеуден кейін пайда болады.",
    statusQueued: "Кезекте",
    statusProcessing: "Өңдеу",
    statusConverting: "Аудионы түрлендіру",
    statusTranscribing: "Сөйлеуді тану",
    statusTranslating: "Аудару",
    statusSummarizing: "Түйіндеме",
    statusDocuments: "Құжаттарды дайындау",
    statusCompleted: "Дайын",
    statusFailed: "Қате",
    msgQueued: "Файл қабылданды. Тапсырма өңдеуді күтуде.",
    msgConverting: "Аудио mono 16 kHz WAV форматына келтірілуде.",
    msgTranscribing: "Модель сөйлеуді танып жатыр.",
    msgTranslating: "Қазақша нұсқа дайындалуда.",
    msgSummarizing: "Қысқа түйіндеме және құрылым жасалуда.",
    msgDocuments: "Құжаттар қалыптастырылуда.",
    msgCompleted: "Дайын. Құжаттарды төменнен жүктеуге болады.",
    msgFailed: "Өңдеу қатемен тоқтады.",
    uploadFailed: "Жүктеу орындалмады.",
    chooseFileFirst: "Алдымен аудио немесе видеофайл таңдаңыз.",
    subtitleIdle: "Субтитрлер сөйлеу кезінде осы жерде пайда болады.",
    speakNow: "Сөйлеңіз. Егер браузер сөйлеуді тануды қолдаса, мәтін осы жерде көрінеді.",
    recordReady: "Жазба жүктеуге дайын.",
    recordingNow: "Жазу жүріп жатыр. Таңдалған микрофонға сөйлеңіз.",
    recordFirst: "Алдымен аудио жазыңыз.",
    sendingRecord: "Жазба серверге жіберілуде. Өңдеуден кейін түйіндеме пайда болады.",
    recordUploaded: "Жазба жүктелді. Қайта жазуға немесе қайта жіберуге болады.",
    micAccessFailed: "Микрофонға қол жеткізу мүмкін болмады.",
    stoppingRecord: "Жазу тоқтатылып, өңдеуге дайындалуда...",
    uploadingRecord: "Жазба жүктелуде...",
    uploadingMicRecord: "Микрофон жазбасы жүктелуде...",
    browserUnsupported: "Браузер микрофоннан жазуды қолдамайды.",
  },
  en: {
    siteLanguage: "Site language",
    brandSubtitle: "Conference and meeting protocols",
    navWelcome: "Home",
    navCapture: "Record",
    navResults: "Result",
    navSettings: "Settings",
    healthChecking: "Checking server...",
    healthOk: "Server is running",
    healthOffline: "Server unavailable",
    heroEyebrow: "Local transcription for institutional work",
    heroTitle: "Record speech or upload audio",
    heroCopy:
      "QazScribe produces transcript text, a Kazakh version, a concise structure, and export documents. Check the microphone first, then send the recording for processing.",
    heroLanguages:
      "Russian, Kazakh, Kyrgyz, Uzbek, Tatar, Tajik, Azerbaijani, Turkmen, Belarusian, and Ukrainian.",
    startWork: "Start",
    chooseMic: "Choose microphone",
    ready: "Ready for test",
    micOrFile: "Microphone or file",
    heroStatusCopy: "After processing, text, summary, and document links will appear.",
    step1Title: "Start microphone recording",
    step1Copy: "Press the microphone button. Allow browser microphone access when prompted.",
    step2Title: "Speak clearly",
    step2Copy:
      "Draft text may appear in the browser in real time. Voice commands for punctuation can help format the text.",
    step3Title: "Or upload an audio file",
    step3Copy:
      "Switch to File mode and upload MP3, WAV, M4A, OGG, WEBM, or MP4. The model processes the recording on your server.",
    step4Title: "Review and export",
    step4Copy: "Review the text, edit it, then download TXT, SRT, VTT, JSON, PDF, DOCX, or HTML.",
    sourceSpeech: "Speech source",
    recordOrFile: "Recording or file",
    mic: "Microphone",
    file: "File",
    micMode: "Microphone mode",
    recordHere: "Record speech here",
    browserRecord: "browser recording",
    speechLanguage: "Speech language",
    refreshMics: "Refresh list",
    livePrompt: "Press Start recording, then speak near the microphone.",
    startRecording: "Start recording",
    stopAndProcess: "Stop and process",
    uploadRecording: "Send recording",
    recordNotStarted: "Recording has not started yet.",
    liveDraft: "Browser draft text",
    waiting: "waiting",
    liveTranscriptPlaceholder:
      "If the browser supports speech recognition, draft text will appear here during recording.",
    fileMode: "File mode",
    uploadReadyFile: "Upload prepared recording",
    fileLabel: "Audio or video file with speech",
    sendToProcessing: "Send for processing",
    supportedFiles: "Supported: mp3, wav, m4a, ogg, webm, mp4.",
    state: "State",
    serverAndTask: "Server and task",
    openResult: "Open result",
    taskInitial: "Upload a file or recording to create a task.",
    processing: "Processing",
    result: "Result",
    taskDetails: "Processing details",
    taskId: "Task ID",
    stage: "Stage",
    progress: "Progress",
    duration: "Duration",
    speakers: "Speakers",
    transcript: "Recognized text",
    detectedLanguage: "Detected language",
    speakerTranscript: "Full speaker transcript",
    kazakhVersion: "Kazakh version",
    fullNotes: "Main full notes",
    shortSummary: "Short summary",
    downloads: "Download result",
    settings: "Settings",
    micAndMode: "Microphone and processing mode",
    input: "Input",
    micChoice: "Microphone selection",
    allowAccess: "Allow access",
    activeMic: "Active microphone",
    draftLanguage: "Draft subtitle language",
    micHelp: "If the required microphone is not visible, press Allow access, then refresh the list.",
    currentMode: "Current mode",
    recognition: "Recognition",
    recognitionValue: "Whisper and Hugging Face ASR on backend",
    cisLanguages: "CIS languages",
    workMode: "Work mode",
    workModeValue: "Local processing on the organization server",
    export: "Export",
    speechAuto: "Auto (device language)",
    noDocs: "Documents will appear after processing is complete.",
    noTask: "None yet",
    taskWaiting: "Waiting",
    transcriptFallback: "Text will appear after model processing.",
    translationFallback: "Translation will appear after processing.",
    speakersFallback: "Speakers will appear after processing.",
    notesFallback: "Notes will appear after processing.",
    summaryFallback: "Short summary will appear after processing.",
    statusQueued: "Queued",
    statusProcessing: "Processing",
    statusConverting: "Audio conversion",
    statusTranscribing: "Speech recognition",
    statusTranslating: "Translation",
    statusSummarizing: "Summary",
    statusDocuments: "Preparing documents",
    statusCompleted: "Completed",
    statusFailed: "Error",
    msgQueued: "File accepted. Task is waiting for processing.",
    msgConverting: "Converting audio to mono 16 kHz WAV.",
    msgTranscribing: "The model is recognizing speech.",
    msgTranslating: "Preparing the Kazakh version.",
    msgSummarizing: "Building short summary and structure.",
    msgDocuments: "Generating documents.",
    msgCompleted: "Done. Documents can be downloaded below.",
    msgFailed: "Processing stopped with an error.",
    uploadFailed: "Upload failed.",
    chooseFileFirst: "Choose an audio or video file first.",
    subtitleIdle: "Subtitles will appear here during speech.",
    speakNow: "Speak. If the browser supports recognition, text will appear here.",
    recordReady: "Recording is ready for upload.",
    recordingNow: "Recording. Speak into the selected microphone.",
    recordFirst: "Record audio first.",
    sendingRecord: "Sending recording to the server. Summary will appear after processing.",
    recordUploaded: "Recording uploaded. You can record again or send it again.",
    micAccessFailed: "Could not access the microphone.",
    stoppingRecord: "Stopping recording and preparing processing...",
    uploadingRecord: "Uploading recording...",
    uploadingMicRecord: "Uploading microphone recording...",
    browserUnsupported: "The browser does not support microphone recording.",
  },
};

const statusLabelKeys = {
  queued: "statusQueued",
  processing: "statusProcessing",
  converting_audio: "statusConverting",
  transcribing: "statusTranscribing",
  translating: "statusTranslating",
  summarizing: "statusSummarizing",
  generating_documents: "statusDocuments",
  completed: "statusCompleted",
  failed: "statusFailed",
  Uploading: "statusProcessing",
  Failed: "statusFailed",
};

const statusMessageKeys = {
  queued: "msgQueued",
  converting_audio: "msgConverting",
  transcribing: "msgTranscribing",
  translating: "msgTranslating",
  summarizing: "msgSummarizing",
  generating_documents: "msgDocuments",
  completed: "msgCompleted",
  failed: "msgFailed",
};

let currentSiteLanguage = "ru";

function t(key) {
  return translations[currentSiteLanguage]?.[key] || translations.ru[key] || key;
}

function statusLabel(status) {
  return t(statusLabelKeys[status]) || status || t("taskWaiting");
}

function statusMessage(status, fallback) {
  const key = statusMessageKeys[status];
  return key ? t(key) : fallback;
}

function detectSiteLanguage() {
  const saved = localStorage.getItem(SITE_LANGUAGE_STORAGE_KEY);
  if (saved && translations[saved]) {
    return saved;
  }

  const browserLanguage = (navigator.language || "ru").slice(0, 2).toLowerCase();
  if (browserLanguage === "kk" || browserLanguage === "en") {
    return browserLanguage;
  }
  return "ru";
}

function renderSiteLanguageOptions() {
  siteLanguageSelect.innerHTML = "";
  siteLanguages.forEach((language) => {
    const option = document.createElement("option");
    option.value = language.code;
    option.textContent = language.label;
    siteLanguageSelect.appendChild(option);
  });
}

function setElementText(selector, key) {
  const element = document.querySelector(selector);
  if (element) {
    element.textContent = t(key);
  }
}

function setElementFallbackValue(selector, key) {
  const element = document.querySelector(selector);
  const fallbackValues = Object.values(translations).map((translation) => translation[key]);
  if (element && (!element.value || fallbackValues.includes(element.value))) {
    element.value = t(key);
  }
}

function applySiteLanguage(languageCode) {
  currentSiteLanguage = translations[languageCode] ? languageCode : "ru";
  localStorage.setItem(SITE_LANGUAGE_STORAGE_KEY, currentSiteLanguage);
  document.documentElement.lang = currentSiteLanguage;
  siteLanguageSelect.value = currentSiteLanguage;

  setElementText(".site-language-label span", "siteLanguage");
  setElementText('[data-screen-target="welcome"]', "navWelcome");
  setElementText('[data-screen-target="capture"]', "navCapture");
  setElementText('[data-screen-target="results"]', "navResults");
  setElementText('[data-screen-target="settings"]', "navSettings");
  setElementText(".brand div span", "brandSubtitle");
  setElementText("#screen-welcome .eyebrow", "heroEyebrow");
  setElementText("#screen-welcome h1", "heroTitle");
  setElementText(".hero-copy", "heroCopy");
  setElementText(".language-line", "heroLanguages");
  setElementText('.button-row [data-screen-target="capture"]', "startWork");
  setElementText('.button-row [data-screen-target="settings"]', "chooseMic");
  setElementText(".hero-status span", "ready");
  setElementText(".hero-status strong", "micOrFile");
  setElementText(".hero-status p", "heroStatusCopy");

  const stepTitles = ["step1Title", "step2Title", "step3Title", "step4Title"];
  const stepCopies = ["step1Copy", "step2Copy", "step3Copy", "step4Copy"];
  document.querySelectorAll(".steps-grid article").forEach((article, index) => {
    article.querySelector("h2").textContent = t(stepTitles[index]);
    article.querySelector("p").textContent = t(stepCopies[index]);
  });

  setElementText("#screen-capture .section-title .eyebrow", "sourceSpeech");
  setElementText("#screen-capture .section-title h1", "recordOrFile");
  setElementText('[data-mode-target="record-panel"]', "mic");
  setElementText('[data-mode-target="file-panel"]', "file");
  setElementText("#record-panel .section-kicker", "micMode");
  setElementText("#record-title", "recordHere");
  setElementText("#record-panel .small-note", "browserRecord");
  setElementText(".mic-select-label span", "mic");
  setElementText(".speech-language-label span", "speechLanguage");
  setElementText("#refresh-mics", "refreshMics");
  setElementText("#record-start", "startRecording");
  setElementText("#record-stop", "stopAndProcess");
  setElementText("#record-upload", "uploadRecording");
  setElementText("#record-status", "recordNotStarted");
  if (!liveSubtitleEl.textContent || liveSubtitleEl.textContent === translations.ru.livePrompt) {
    liveSubtitleEl.textContent = t("livePrompt");
  }
  setElementText(".live-box h3", "liveDraft");
  if (speechStatusEl.textContent === translations.ru.waiting || speechStatusEl.textContent === "ожидание") {
    speechStatusEl.textContent = t("waiting");
  }
  if (liveTranscriptEl.textContent === translations.ru.liveTranscriptPlaceholder) {
    liveTranscriptEl.textContent = t("liveTranscriptPlaceholder");
  }

  setElementText("#file-panel .section-kicker", "fileMode");
  setElementText("#upload-title", "uploadReadyFile");
  setElementText('label[for="audio-file"]', "fileLabel");
  setElementText("#upload-button", "sendToProcessing");
  setElementText("#file-panel .muted", "supportedFiles");
  setElementText(".status-panel .section-kicker", "state");
  setElementText("#status-title", "serverAndTask");
  setElementText(".status-panel [data-screen-target='results']", "openResult");
  if (!taskMessageEl.textContent || taskMessageEl.textContent === translations.ru.taskInitial) {
    taskMessageEl.textContent = t("taskInitial");
  }

  setElementText("#screen-results .section-title .eyebrow", "processing");
  setElementText("#screen-results .section-title h1", "result");
  setElementText("#task-title", "taskDetails");
  setElementText(".status-grid > div:nth-child(1) .status-label", "taskId");
  setElementText(".status-grid > div:nth-child(2) .status-label", "stage");
  setElementText(".status-grid > div:nth-child(3) .status-label", "progress");
  setElementText(".status-grid > div:nth-child(4) .status-label", "duration");
  setElementText(".status-grid > div:nth-child(5) .status-label", "speakers");
  setElementText("#result-title", "transcript");
  setElementText("#result-title + p .status-label", "detectedLanguage");
  setElementText("#speakers-title", "speakerTranscript");
  setElementText("#translation-title", "kazakhVersion");
  setElementText("#notes-title", "fullNotes");
  setElementText("#summary-title", "shortSummary");
  setElementText("#downloads-title", "downloads");
  setElementFallbackValue("#transcript-preview", "transcriptFallback");
  setElementFallbackValue("#speaker-preview", "speakersFallback");
  setElementFallbackValue("#translation-preview", "translationFallback");
  setElementFallbackValue("#detailed-summary-preview", "notesFallback");
  setElementFallbackValue("#summary-preview", "summaryFallback");

  setElementText("#screen-settings .section-title .eyebrow", "settings");
  setElementText("#screen-settings .section-title h1", "micAndMode");
  setElementText("#screen-settings .panel:first-of-type .section-kicker", "input");
  setElementText("#screen-settings .panel:first-of-type h2", "micChoice");
  setElementText("#request-mic-access", "allowAccess");
  setElementText(".settings-mic-label span", "activeMic");
  setElementText(".settings-language-label span", "draftLanguage");
  if (micHelpEl.textContent === translations.ru.micHelp) {
    micHelpEl.textContent = t("micHelp");
  }
  setElementText("#screen-settings .panel:nth-of-type(2) h2", "currentMode");
  setElementText(".settings-list > div:nth-child(1) .status-label", "recognition");
  setElementText(".settings-list > div:nth-child(1) strong", "recognitionValue");
  setElementText(".settings-list > div:nth-child(2) .status-label", "cisLanguages");
  setElementText(".settings-list > div:nth-child(3) .status-label", "workMode");
  setElementText(".settings-list > div:nth-child(3) strong", "workModeValue");
  setElementText(".settings-list > div:nth-child(4) .status-label", "export");

  renderLanguageOptions();
}

function showScreen(screenName) {
  screens.forEach((screen) => {
    screen.classList.toggle("active", screen.id === `screen-${screenName}`);
  });
  document.querySelectorAll(".nav-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.screenTarget === screenName);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showMode(panelId) {
  modePanels.forEach((panel) => {
    panel.classList.toggle("active", panel.id === panelId);
  });
  modeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.modeTarget === panelId);
  });
}

function setTextValue(element, value, fallback) {
  if (!element) {
    return;
  }
  element.value = value || fallback;
}

function formatDuration(seconds) {
  if (!seconds) {
    return t("noTask");
  }
  const total = Math.round(seconds);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

async function readResponsePayload(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return {
    detail: text || `Сервер вернул ${response.status}`,
  };
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`Проверка сервера вернула ${response.status}`);
    }

    const data = await readResponsePayload(response);
    healthStatus.textContent = data.status === "ok" ? t("healthOk") : data.status;
    healthStatus.classList.remove("error");
  } catch (error) {
    healthStatus.textContent = t("healthOffline");
    healthStatus.classList.add("error");
    console.error(error);
  }
}

function setTaskView({
  taskId,
  status,
  progress,
  message,
  error,
  detectedLanguage,
  transcriptPreview,
  translationPreview,
  summaryPreview,
  detailedSummaryPreview,
  speakerPreview,
  recordingDurationSeconds,
  speakerCount,
  downloads,
}) {
  if (taskId !== undefined) {
    taskIdEl.textContent = taskId || t("noTask");
  }
  if (status !== undefined) {
    taskStatusEl.textContent = statusLabel(status);
  }
  if (progress !== undefined) {
    const value = progress || 0;
    taskProgressEl.textContent = `${value}%`;
    progressBar.style.width = `${value}%`;
  }
  if (recordingDurationSeconds !== undefined) {
    taskDurationEl.textContent = formatDuration(recordingDurationSeconds);
  }
  if (speakerCount !== undefined) {
    taskSpeakersEl.textContent = speakerCount ? `${speakerCount}` : t("noTask");
  }
  if (message !== undefined) {
    taskMessageEl.textContent = message || "";
  }
  if (detectedLanguage !== undefined) {
    detectedLanguageEl.textContent = detectedLanguage || t("noTask");
  }
  if (transcriptPreview !== undefined) {
    setTextValue(
      transcriptPreviewEl,
      transcriptPreview,
      t("transcriptFallback"),
    );
  }
  if (translationPreview !== undefined) {
    setTextValue(translationPreviewEl, translationPreview, t("translationFallback"));
  }
  if (speakerPreview !== undefined) {
    setTextValue(speakerPreviewEl, speakerPreview, t("speakersFallback"));
  }
  if (detailedSummaryPreview !== undefined) {
    setTextValue(
      detailedSummaryPreviewEl,
      detailedSummaryPreview,
      t("notesFallback"),
    );
  }
  if (summaryPreview !== undefined) {
    setTextValue(summaryPreviewEl, summaryPreview, t("summaryFallback"));
  }
  if (downloads !== undefined) {
    renderDownloads(downloads);
  }

  if (error) {
    taskErrorEl.textContent = error;
    taskErrorEl.hidden = false;
  } else {
    taskErrorEl.textContent = "";
    taskErrorEl.hidden = true;
  }
}

function renderDownloads(downloads) {
  downloadLinksEl.innerHTML = "";

  if (!downloads || Object.keys(downloads).length === 0) {
    const placeholder = document.createElement("span");
    placeholder.className = "muted";
    placeholder.textContent = t("noDocs");
    downloadLinksEl.appendChild(placeholder);
    return;
  }

  const labels = {
    txt: "TXT",
    srt: "SRT",
    vtt: "VTT",
    json: "JSON",
    pdf: "PDF",
    docx: "DOCX",
    html: "HTML",
  };

  Object.entries(labels).forEach(([format, label]) => {
    if (!downloads[format]) {
      return;
    }

    const link = document.createElement("a");
    link.className = "download-link";
    link.href = downloads[format];
    link.textContent = label;
    link.target = "_blank";
    link.rel = "noopener";
    downloadLinksEl.appendChild(link);
  });
}

async function loadTask(taskId) {
  const response = await fetch(`/api/tasks/${taskId}`);
  if (!response.ok) {
    throw new Error(`Не удалось получить статус задачи: ${response.status}`);
  }

  const task = await readResponsePayload(response);
  setTaskView({
    taskId: task.task_id,
    status: task.status,
    progress: task.progress,
    message: statusMessage(task.status, task.message),
    error: task.error,
    detectedLanguage: task.detected_language,
    transcriptPreview: task.transcript_preview,
    translationPreview: task.translation_preview,
    summaryPreview: task.summary_preview,
    detailedSummaryPreview: task.detailed_summary_preview,
    speakerPreview: task.speaker_preview,
    recordingDurationSeconds: task.recording_duration_seconds,
    speakerCount: task.speaker_count,
    downloads: task.downloads,
  });

  if (task.status === "completed" || task.status === "failed") {
    clearInterval(pollTimer);
    pollTimer = null;
    showScreen("results");
  }
}

function startPolling(taskId) {
  if (pollTimer) {
    clearInterval(pollTimer);
  }

  loadTask(taskId).catch((error) => {
    setTaskView({ error: error.message });
  });

  pollTimer = setInterval(() => {
    loadTask(taskId).catch((error) => {
      clearInterval(pollTimer);
      pollTimer = null;
      setTaskView({ error: error.message });
    });
  }, 1500);
}

async function uploadFile(file, button, uploadMessage) {
  const formData = new FormData();
  formData.append("file", file);

  button.disabled = true;
  showScreen("capture");
  setTaskView({
    taskId: "",
    status: "Uploading",
    progress: 0,
    message: uploadMessage,
    error: "",
    downloads: null,
  });

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await readResponsePayload(response);
    if (!response.ok) {
      throw new Error(data.detail || `${t("uploadFailed")}: ${response.status}`);
    }

    setTaskView({
      taskId: data.task_id,
      status: data.status,
      progress: 0,
      message: "Файл принят. Обработка началась.",
      error: "",
    });
    startPolling(data.task_id);
  } catch (error) {
    setTaskView({
      status: "Failed",
      message: t("uploadFailed"),
      error: error.message,
    });
  } finally {
    button.disabled = false;
  }
}

async function uploadAudio(event) {
  event.preventDefault();

  const file = audioFileInput.files[0];
  if (!file) {
    setTaskView({ error: t("chooseFileFirst") });
    showScreen("capture");
    showMode("file-panel");
    return;
  }

  await uploadFile(file, uploadButton, "Загружаю файл на сервер...");
}

function selectedMicId() {
  return micSelect.value || settingsMicSelect.value || "";
}

function browserSpeechLanguage() {
  const browserLanguage = navigator.language || "ru-RU";
  const exactMatch = speechLanguages.find((language) => language.code === browserLanguage);
  if (exactMatch) {
    return exactMatch.code;
  }
  const languagePrefix = browserLanguage.slice(0, 2).toLowerCase();
  const prefixMatch = speechLanguages.find((language) =>
    language.code.toLowerCase().startsWith(`${languagePrefix}-`),
  );
  return prefixMatch ? prefixMatch.code : "ru-RU";
}

function selectedSpeechLanguage() {
  const selected = languageSelect.value || settingsLanguageSelect.value || "auto";
  return selected === "auto" ? browserSpeechLanguage() : selected;
}

function saveSelectedMic(deviceId) {
  if (deviceId) {
    localStorage.setItem(MIC_STORAGE_KEY, deviceId);
  } else {
    localStorage.removeItem(MIC_STORAGE_KEY);
  }
}

function rememberMicPermissionGranted() {
  localStorage.setItem(MIC_PERMISSION_STORAGE_KEY, "true");
}

function syncMicSelects(deviceId) {
  [micSelect, settingsMicSelect].forEach((select) => {
    if (select.value !== deviceId) {
      select.value = deviceId;
    }
  });
}

function saveSelectedLanguage(languageCode) {
  localStorage.setItem(LANGUAGE_STORAGE_KEY, languageCode || "ru-RU");
}

function syncLanguageSelects(languageCode) {
  [languageSelect, settingsLanguageSelect].forEach((select) => {
    if (select.value !== languageCode) {
      select.value = languageCode;
    }
  });
}

function renderLanguageOptions() {
  const rememberedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY) || "auto";
  [languageSelect, settingsLanguageSelect].forEach((select) => {
    select.innerHTML = "";
    speechLanguages.forEach((language) => {
      const option = document.createElement("option");
      option.value = language.code;
      option.textContent = language.labelKey ? t(language.labelKey) : language.label;
      select.appendChild(option);
    });
  });
  const selected = speechLanguages.some((language) => language.code === rememberedLanguage)
    ? rememberedLanguage
    : "auto";
  syncLanguageSelects(selected);
  saveSelectedLanguage(selected);
}

function renderMicOptions(devices) {
  const rememberedId = localStorage.getItem(MIC_STORAGE_KEY) || "";
  const audioInputs = devices.filter((device) => device.kind === "audioinput");
  const options = audioInputs.length
    ? audioInputs
    : [{ deviceId: "", label: "Микрофон по умолчанию" }];

  [micSelect, settingsMicSelect].forEach((select) => {
    select.innerHTML = "";
    options.forEach((device, index) => {
      const option = document.createElement("option");
      option.value = device.deviceId;
      option.textContent = device.label || `Микрофон ${index + 1}`;
      select.appendChild(option);
    });
  });

  const selected = options.some((device) => device.deviceId === rememberedId)
    ? rememberedId
    : options[0].deviceId;
  syncMicSelects(selected);
  saveSelectedMic(selected);
}

async function loadMicrophones() {
  if (!navigator.mediaDevices?.enumerateDevices) {
    micHelpEl.textContent = "Этот браузер не показывает список микрофонов.";
    return;
  }

  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    renderMicOptions(devices);
    const permissionWasGranted = localStorage.getItem(MIC_PERMISSION_STORAGE_KEY) === "true";
    micHelpEl.textContent = permissionWasGranted
      ? "Микрофон выбран. Если браузер снова спрашивает доступ, это ограничение браузера."
      : "Выбранный микрофон сохранится в этом браузере.";
  } catch (error) {
    micHelpEl.textContent = `Не удалось получить список микрофонов: ${error.message}`;
  }
}

async function requestMicrophoneAccess() {
  if (!navigator.mediaDevices?.getUserMedia) {
    micHelpEl.textContent = "Браузер не поддерживает доступ к микрофону.";
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    rememberMicPermissionGranted();
    stream.getTracks().forEach((track) => track.stop());
    await loadMicrophones();
  } catch (error) {
    micHelpEl.textContent = `Доступ к микрофону не получен: ${error.message}`;
  }
}

async function getMicrophoneStream(deviceId) {
  if (!deviceId) {
    return navigator.mediaDevices.getUserMedia({ audio: true });
  }

  try {
    return await navigator.mediaDevices.getUserMedia({
      audio: { deviceId: { exact: deviceId } },
    });
  } catch (error) {
    if (error.name !== "OverconstrainedError" && error.name !== "NotFoundError") {
      throw error;
    }
    saveSelectedMic("");
    syncMicSelects("");
    return navigator.mediaDevices.getUserMedia({ audio: true });
  }
}

function setRecordingState(state, message) {
  recordStatusEl.textContent = message;

  if (state === "unsupported") {
    recordStartButton.disabled = true;
    recordStopButton.disabled = true;
    recordUploadButton.disabled = true;
    return;
  }

  recordStartButton.disabled = state === "recording" || state === "stopping" || state === "uploading";
  recordStopButton.disabled = state !== "recording";
  recordUploadButton.disabled = state !== "ready";
}

function getRecorderOptions() {
  const preferredTypes = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
  ];

  const mimeType = preferredTypes.find((type) => MediaRecorder.isTypeSupported(type));
  return mimeType ? { mimeType } : undefined;
}

function initializeMicMeter() {
  micMeterEl.innerHTML = "";
  for (let index = 0; index < 36; index += 1) {
    const bar = document.createElement("span");
    bar.className = "meter-bar";
    bar.style.height = "10px";
    micMeterEl.appendChild(bar);
  }
}

function stopMicMeter() {
  if (meterFrame) {
    cancelAnimationFrame(meterFrame);
    meterFrame = null;
  }
  if (audioContext) {
    audioContext.close().catch(() => {});
    audioContext = null;
  }
  analyser = null;
  meterSource = null;
  meterData = null;
  recordingDotEl.classList.remove("active");
  micMeterEl.querySelectorAll(".meter-bar").forEach((bar) => {
    bar.style.height = "10px";
    bar.style.opacity = "0.54";
  });
}

function drawMicMeter() {
  if (!analyser || !meterData) {
    return;
  }

  analyser.getByteFrequencyData(meterData);
  const bars = Array.from(micMeterEl.querySelectorAll(".meter-bar"));
  bars.forEach((bar, index) => {
    const bucketSize = Math.max(1, Math.floor(meterData.length / bars.length));
    const start = index * bucketSize;
    const slice = meterData.slice(start, start + bucketSize);
    const average = slice.reduce((sum, value) => sum + value, 0) / slice.length || 0;
    const height = 10 + (average / 255) * 78;
    bar.style.height = `${height}px`;
    bar.style.opacity = `${0.42 + (average / 255) * 0.58}`;
  });

  meterFrame = requestAnimationFrame(drawMicMeter);
}

function startMicMeter(stream) {
  stopMicMeter();
  const Context = window.AudioContext || window.webkitAudioContext;
  if (!Context) {
    return;
  }

  audioContext = new Context();
  meterSource = audioContext.createMediaStreamSource(stream);
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  analyser.smoothingTimeConstant = 0.72;
  meterSource.connect(analyser);
  meterData = new Uint8Array(analyser.frequencyBinCount);
  recordingDotEl.classList.add("active");
  drawMicMeter();
}

function updateLiveSubtitle(text) {
  const cleaned = normalizeSpeechText(text || "");
  const compact = cleaned.replace(/\s+/g, " ").trim();
  if (!compact) {
    liveSubtitleEl.textContent = t("subtitleIdle");
    return;
  }
  const sentences = compact.match(/[^.!?\n]+[.!?]?/g) || [compact];
  liveSubtitleEl.textContent = sentences.slice(-2).join(" ").trim();
}

function normalizeSpeechText(text) {
  return text
    .replace(/\bточка\b/gi, ".")
    .replace(/\bзапятая\b/gi, ",")
    .replace(/\bновый абзац\b/gi, "\n\n")
    .replace(/\s+([.,!?])/g, "$1")
    .replace(/[ \t]+\n/g, "\n")
    .trim();
}

function createSpeechRecognition() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    speechStatusEl.textContent = "не поддерживается";
    return null;
  }

  const recognition = new Recognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = selectedSpeechLanguage();
  recognition.addEventListener("result", (event) => {
    let interimText = "";
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const text = event.results[index][0].transcript;
      if (event.results[index].isFinal) {
        speechFinalText = `${speechFinalText} ${text}`;
      } else {
        interimText = `${interimText} ${text}`;
      }
    }
    const combinedText = normalizeSpeechText(`${speechFinalText} ${interimText}`);
    liveTranscriptEl.textContent = combinedText;
    updateLiveSubtitle(combinedText);
  });
  recognition.addEventListener("start", () => {
    speechStatusEl.textContent = "слушает";
  });
  recognition.addEventListener("end", () => {
    speechStatusEl.textContent = "остановлено";
  });
  recognition.addEventListener("error", () => {
    speechStatusEl.textContent = "черновик недоступен";
  });
  return recognition;
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    setRecordingState("unsupported", "Браузер не поддерживает запись с микрофона.");
    return;
  }

  try {
    recordedChunks = [];
    recordedBlob = null;
    autoUploadAfterStop = false;
    speechFinalText = "";
    liveTranscriptEl.textContent = t("speakNow");
    liveSubtitleEl.textContent = "Слушаю микрофон...";
    recordPreview.hidden = true;
    recordPreview.removeAttribute("src");

    const deviceId = selectedMicId();
    recordingStream = await getMicrophoneStream(deviceId);
    rememberMicPermissionGranted();
    startMicMeter(recordingStream);
    mediaRecorder = new MediaRecorder(recordingStream, getRecorderOptions());

    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    });

    mediaRecorder.addEventListener("stop", () => {
      const mimeType = mediaRecorder.mimeType || "audio/webm";
      recordedBlob = new Blob(recordedChunks, { type: mimeType });
      const previewUrl = URL.createObjectURL(recordedBlob);
      recordPreview.src = previewUrl;
      recordPreview.hidden = false;

      recordingStream.getTracks().forEach((track) => track.stop());
      recordingStream = null;
      mediaRecorder = null;
      stopMicMeter();

      if (speechRecognition) {
        try {
          speechRecognition.stop();
        } catch (error) {
          console.debug("Speech recognition was already stopped.", error);
        }
      }

      setRecordingState("ready", t("recordReady"));
      if (autoUploadAfterStop) {
        autoUploadAfterStop = false;
        uploadRecording();
      }
    });

    mediaRecorder.start();
    speechRecognition = createSpeechRecognition();
    if (speechRecognition) {
      speechRecognition.start();
    }
    setRecordingState("recording", t("recordingNow"));
  } catch (error) {
    setRecordingState("idle", t("micAccessFailed"));
    setTaskView({ error: error.message });
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    autoUploadAfterStop = true;
    mediaRecorder.stop();
    setRecordingState("stopping", t("stoppingRecord"));
  }
}

async function uploadRecording() {
  if (!recordedBlob) {
    setTaskView({ error: t("recordFirst") });
    return;
  }

  const extension = recordedBlob.type.includes("ogg") ? "ogg" : "webm";
  const file = new File([recordedBlob], `browser-recording.${extension}`, {
    type: recordedBlob.type || "audio/webm",
  });

  setRecordingState("uploading", t("uploadingRecord"));
  liveSubtitleEl.textContent = t("sendingRecord");
  await uploadFile(file, recordUploadButton, t("uploadingMicRecord"));
  setRecordingState("ready", t("recordUploaded"));
}

navButtons.forEach((button) => {
  button.addEventListener("click", () => showScreen(button.dataset.screenTarget));
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => showMode(button.dataset.modeTarget));
});

uploadForm.addEventListener("submit", uploadAudio);
recordStartButton.addEventListener("click", startRecording);
recordStopButton.addEventListener("click", stopRecording);
recordUploadButton.addEventListener("click", uploadRecording);
refreshMicsButton.addEventListener("click", loadMicrophones);
requestMicAccessButton.addEventListener("click", requestMicrophoneAccess);

[micSelect, settingsMicSelect].forEach((select) => {
  select.addEventListener("change", () => {
    saveSelectedMic(select.value);
    syncMicSelects(select.value);
  });
});

[languageSelect, settingsLanguageSelect].forEach((select) => {
  select.addEventListener("change", () => {
    saveSelectedLanguage(select.value);
    syncLanguageSelects(select.value);
  });
});

if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
  setRecordingState("unsupported", t("browserUnsupported"));
}

renderSiteLanguageOptions();
applySiteLanguage(detectSiteLanguage());
siteLanguageSelect.addEventListener("change", () => applySiteLanguage(siteLanguageSelect.value));
loadHealth();
initializeMicMeter();
loadMicrophones();
