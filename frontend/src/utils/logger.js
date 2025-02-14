// 定义日志级别
const LOG_LEVEL = {
    DEBUG: 0,
    INFO: 1,
    WARNING: 2,
    ERROR: 3
};

// 先调整日志级别为 DEBUG，方便排查问题
const CURRENT_LEVEL = LOG_LEVEL.DEBUG;  // 临时修改

// 日志工具类
export const logger = {
    debug: (...args) => {
        if (CURRENT_LEVEL <= LOG_LEVEL.DEBUG) {
            console.debug(...args);
        }
    },
    
    info: (...args) => {
        if (CURRENT_LEVEL <= LOG_LEVEL.INFO) {
            console.info(...args);
        }
    },
    
    warn: (...args) => {
        if (CURRENT_LEVEL <= LOG_LEVEL.WARNING) {
            console.warn(...args);
        }
    },
    
    error: (...args) => {
        if (CURRENT_LEVEL <= LOG_LEVEL.ERROR) {
            console.error(...args);
        }
    },
    
    // 添加音频相关的专门日志方法
    audioLoad: (message, data = null) => {
        const logMessage = `[Audio Load] ${message}`;
        if (data) {
            console.group(logMessage);
            console.debug(data);
            console.groupEnd();
        } else {
            console.debug(logMessage);
        }
    },
    
    // 添加错误追踪
    trackError: (error, context) => {
        console.group(`[Error] ${context}`);
        console.error('Message:', error.message);
        console.error('Stack:', error.stack);
        if (error.response) {
            console.error('Response:', error.response);
        }
        console.groupEnd();
    }
};

// 在生产环境中完全禁用 console.log
if (process.env.NODE_ENV === 'production') {
    console.log = () => {};
    console.debug = () => {};
    console.info = () => {};
} 