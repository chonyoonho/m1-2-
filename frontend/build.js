// Vercel 빌드 시 API_BASE_URL 환경 변수 값을 js/config.js에 주입한다. (외부 패키지 의존성 없음)
const fs = require("fs");
const path = require("path");

const apiBaseUrl = process.env.API_BASE_URL || "http://localhost:8000";

const content = `// 빌드 시 자동 생성된 파일입니다. 직접 수정하지 마세요. (build.js 참고)
window.APP_CONFIG = {
  API_BASE_URL: "${apiBaseUrl}",
};
`;

const outPath = path.join(__dirname, "js", "config.js");
fs.writeFileSync(outPath, content, "utf-8");
console.log(`[build.js] API_BASE_URL=${apiBaseUrl} 로 ${outPath} 생성 완료`);
