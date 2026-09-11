<template>
  <main class="workspace">
    <aside class="sidebar">
      <div class="brand-block">
        <div class="brand-mark">IQ</div>
        <div>
          <p class="eyebrow">Overseas Ops Intelligence</p>
          <h1>海外运营智数平台</h1>
        </div>
      </div>

      <section class="panel">
        <h2>核心指标</h2>
        <div class="metric-grid">
          <span v-for="metric in metrics" :key="metric">{{ metric }}</span>
        </div>
      </section>

      <section class="panel">
        <h2>常用分析</h2>
        <button
          v-for="item in examples"
          :key="item"
          class="example-button"
          type="button"
          @click="askExample(item)"
        >
          {{ item }}
        </button>
      </section>
    </aside>

    <section class="chat-shell">
      <header class="chat-header">
        <div>
          <p class="eyebrow">Operations Analytics</p>
          <h2>用自然语言查询海外市场、渠道、版本和收入表现</h2>
        </div>
        <div class="status-pill">指标口径中心已接入</div>
      </header>

      <div ref="messagesEl" class="messages">
        <div v-if="messages.length === 0" class="empty-state">
          <p class="empty-title">选择一个运营问题，或直接输入你的问数需求。</p>
          <p class="empty-copy">
            当前数据域覆盖 DAU、留存、订阅、广告、崩溃率和应用商店评分。
          </p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-row', msg.role]"
        >
          <div v-if="msg.role === 'assistant'" class="avatar">AI</div>

          <div class="bubble">
            <div v-if="msg.type === 'text'">
              {{ msg.content }}
            </div>

            <div v-else-if="msg.type === 'steps'" class="steps">
              <div v-for="(step, sIdx) in msg.steps" :key="sIdx" class="step">
                <span class="dot" :class="step.status"></span>
                <span>{{ step.text }}</span>
              </div>
            </div>

            <div v-else-if="msg.type === 'table'" class="table-wrap">
              <table class="result-table">
                <thead>
                  <tr>
                    <th v-for="col in msg.columns" :key="col">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rIdx) in msg.rows" :key="rIdx">
                    <td v-for="col in msg.columns" :key="col">
                      {{ row[col] }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-else-if="msg.type === 'error'" class="error-text">
              {{ msg.content }}
            </div>
          </div>

          <div v-if="msg.role === 'user'" class="avatar">OP</div>
        </div>
      </div>

      <form class="input-wrapper" @submit.prevent="sendQuestion">
        <input
          v-model="question"
          placeholder="例如：过去30天美国市场 DAU 和订阅转化率趋势"
        />
        <button type="submit" :disabled="loading || !question.trim()">
          {{ loading ? "查询中" : "发送" }}
        </button>
      </form>
    </section>
  </main>
</template>

<script setup>
import { nextTick, ref } from "vue";

const API_URL = "/api/query";

const metrics = [
  "DAU",
  "D1 Retention",
  "Paid Conversion",
  "Subscription Revenue",
  "Ad Revenue",
  "Crash Rate",
  "Bad Review Rate",
  "Average Rating",
];

const examples = [
  "过去30天美国市场 DAU 和订阅转化率趋势",
  "各国家广告收入排名前10",
  "3.2.0版本上线后一周崩溃率是否上升",
  "TikTok Ads渠道的新用户次日留存怎么样",
  "西班牙语市场差评率最高来自哪些版本",
  "按渠道对比 AI Chat Assistant 的 ARPDAU",
];

const question = ref("");
const loading = ref(false);
const messages = ref([]);
const messagesEl = ref(null);

function scrollToBottom() {
  const el = messagesEl.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

function askExample(item) {
  if (loading.value) return;
  question.value = item;
  sendQuestion();
}

async function sendQuestion() {
  if (!question.value.trim() || loading.value) return;

  const q = question.value.trim();
  question.value = "";
  loading.value = true;

  messages.value.push({ role: "user", type: "text", content: q });

  const stepIndex =
    messages.value.push({
      role: "assistant",
      type: "steps",
      steps: [],
    }) - 1;

  await nextTick();
  scrollToBottom();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
    });

    if (!response.body) throw new Error("服务器未返回流式结果");

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop();

      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data:")) continue;

        let data;
        try {
          data = JSON.parse(line.replace(/^data:\s*/, ""));
        } catch {
          continue;
        }

        const steps = messages.value[stepIndex].steps;

        if (data.stage) {
          const last = steps.at(-1);
          if (last && last.status === "running") last.status = "success";
          steps.push({ text: data.stage, status: "running" });
        } else if (data.error) {
          const last = steps.at(-1);
          if (last) last.status = "error";
          messages.value.push({
            role: "assistant",
            type: "error",
            content: data.error,
          });
        } else if (Array.isArray(data.result)) {
          const last = steps.at(-1);
          if (last) last.status = "success";
          messages.value.push({
            role: "assistant",
            type: "table",
            columns: Object.keys(data.result[0] || {}),
            rows: data.result,
          });
        }

        await nextTick();
        scrollToBottom();
      }
    }
  } catch (e) {
    messages.value.push({
      role: "assistant",
      type: "error",
      content: e?.message || "请求失败",
    });
  } finally {
    loading.value = false;
    await nextTick();
    scrollToBottom();
  }
}
</script>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  height: 100%;
  margin: 0;
}

:global(body) {
  min-width: 320px;
  background: #f3f5f7;
  color: #17202a;
}

:global(*) {
  box-sizing: border-box;
}

button,
input {
  font: inherit;
}

.workspace {
  height: 100%;
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  background:
    linear-gradient(180deg, rgba(23, 32, 42, 0.04), transparent 220px),
    #f3f5f7;
}

.sidebar {
  height: 100%;
  overflow-y: auto;
  padding: 28px 24px;
  background: #17202a;
  color: #f8fafc;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-block {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 28px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  background: #2dd4bf;
  color: #0f172a;
  font-weight: 800;
}

.eyebrow {
  margin: 0 0 4px;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.sidebar .eyebrow {
  color: #9ca3af;
}

h1,
h2 {
  margin: 0;
  letter-spacing: 0;
}

h1 {
  font-size: 20px;
  line-height: 1.25;
}

.panel {
  padding: 18px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
}

.panel h2 {
  margin-bottom: 12px;
  font-size: 15px;
  color: #e5e7eb;
}

.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.metric-grid span {
  min-height: 32px;
  display: flex;
  align-items: center;
  padding: 7px 9px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  color: #dbeafe;
  font-size: 12px;
}

.example-button {
  width: 100%;
  min-height: 42px;
  margin-bottom: 9px;
  padding: 9px 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: #f8fafc;
  text-align: left;
  line-height: 1.35;
  cursor: pointer;
}

.example-button:hover {
  border-color: #2dd4bf;
  background: rgba(45, 212, 191, 0.12);
}

.chat-shell {
  min-width: 0;
  height: 100%;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  padding: 28px 32px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
}

.chat-header h2 {
  font-size: 22px;
  line-height: 1.35;
  color: #111827;
}

.status-pill {
  flex: 0 0 auto;
  padding: 7px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background: #ffffff;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.messages {
  min-height: 0;
  overflow-y: auto;
  padding: 28px 32px;
}

.empty-state {
  max-width: 620px;
  padding: 28px;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.62);
}

.empty-title {
  margin: 0 0 8px;
  color: #111827;
  font-size: 18px;
  font-weight: 750;
}

.empty-copy {
  margin: 0;
  color: #64748b;
}

.message-row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.message-row.assistant {
  justify-content: flex-start;
}

.message-row.user {
  justify-content: flex-end;
}

.avatar {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 8px;
  background: #e2e8f0;
  color: #334155;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
}

.message-row.user .avatar {
  background: #ccfbf1;
  color: #115e59;
}

.bubble {
  max-width: min(920px, 78%);
  padding: 13px 15px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.message-row.user .bubble {
  background: #ecfeff;
  border-color: #a5f3fc;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #334155;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex: 0 0 9px;
}

.dot.running {
  background: #f59e0b;
}

.dot.success {
  background: #14b8a6;
}

.dot.error {
  background: #ef4444;
}

.table-wrap {
  max-width: 100%;
  overflow-x: auto;
}

.result-table {
  width: max-content;
  min-width: 100%;
  border-collapse: collapse;
}

.result-table th,
.result-table td {
  border-bottom: 1px solid #e5e7eb;
  padding: 8px 12px;
  white-space: nowrap;
  font-size: 13px;
  text-align: left;
}

.result-table th {
  background: #f8fafc;
  color: #334155;
  font-weight: 750;
  position: sticky;
  top: 0;
}

.error-text {
  color: #b91c1c;
  font-weight: 700;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  padding: 18px 32px 24px;
  border-top: 1px solid #e5e7eb;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
}

.input-wrapper input {
  flex: 1;
  min-width: 0;
  height: 46px;
  padding: 0 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  outline: none;
  background: #ffffff;
  color: #111827;
}

.input-wrapper input:focus {
  border-color: #14b8a6;
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.16);
}

.input-wrapper button {
  width: 92px;
  height: 46px;
  border: none;
  border-radius: 8px;
  background: #0f766e;
  color: #ffffff;
  cursor: pointer;
  font-weight: 750;
}

.input-wrapper button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

@media (max-width: 880px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .sidebar {
    height: auto;
    max-height: 42vh;
  }

  .chat-shell {
    height: 58vh;
  }

  .chat-header,
  .messages,
  .input-wrapper {
    padding-left: 18px;
    padding-right: 18px;
  }

  .chat-header {
    flex-direction: column;
  }

  .bubble {
    max-width: calc(100vw - 92px);
  }
}
</style>
