# Phase 2 外部服務驗收

## 外部 LLM

- 缺少 API key／未開啟 gate：PASS。`POST /api/chat` 回 503、`code=LLM_NOT_CONFIGURED`，不回傳偽成功。
- 明確後端閘門：PASS。只有 `JUDICIAL3_ALLOW_EXTERNAL_AI === 'true'` 且 key 同時存在才建立 client。
- caller 自訂 system prompt：已移除；使用固定 server-side instruction。
- 輸入 schema：1–50 筆，僅 user/assistant，非空字串且每筆最多 20,000 字；不合法回 400。
- 403／服務錯誤：程式回 503 `LLM_UNAVAILABLE`；實際供應商故障注入 NOT_RUN。
- 無效 key、timeout、429、500、空白回應、格式錯誤：NOT_RUN，未提供測試憑證且沒有 injectable transport。
- 個資脫敏、用途同意與 egress audit：FAIL，尚未實作；因此即使有 key 也不具備傳送真實案件資格。

## 法律檢索

application runtime 沒有法律檢索 client、版本查證或來源不可用狀態機，結果為 FAIL。候選法條若資料庫沒有已核對來源，現在只保存正確 law/article 並標示 `UNKNOWN（官方版本尚未核對）`，不再錯綁第一筆法條，也不宣稱現行有效。

法律服務的無結果、不可用、來源衝突與模型不一致測試均為 BLOCKED，前置條件是先實作去識別化 retrieval adapter、來源版本欄位與 injectable failure transport。
