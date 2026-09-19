<script setup>
import { ref } from 'vue'
import StudentList from '@/components/StudentList.vue'
import StudentForm from '@/components/StudentForm.vue'
import ToastNotification from '@/components/ToastNotification.vue'

const showForm = ref(false)
const editingStudent = ref(null)
const listRef = ref(null)
const toasts = ref([])

function addToast(message, type = 'success') {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    dismissToast(id)
  }, 4000)
}

function dismissToast(id) {
  toasts.value = toasts.value.filter((t) => t.id !== id)
}

function handleToastFromList(payload) {
  addToast(payload.message, payload.type)
}

function openCreateForm() {
  editingStudent.value = null
  showForm.value = true
}

function openEditForm(student) {
  editingStudent.value = { ...student }
  showForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onSaved(actionType) {
  showForm.value = false
  const msg = actionType === 'update' ? 'Student record updated.' : 'Student created successfully.'
  addToast(msg, 'success')
  editingStudent.value = null
  listRef.value?.fetchStudents()
}

function onCancel() {
  showForm.value = false
  editingStudent.value = null
}
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="header-left">
        <div class="logo">🎓</div>
        <div>
          <h1>Student Management System</h1>
          <p class="header-subtitle">Internal Student Directory & Administration</p>
        </div>
      </div>
      <button v-if="!showForm" @click="openCreateForm" class="btn btn-primary btn-add">
        <span class="btn-icon">+</span> Add Student
      </button>
    </header>

    <main class="app-main">
      <transition name="slide-fade">
        <StudentForm
          v-if="showForm"
          :student="editingStudent"
          @saved="onSaved"
          @cancel="onCancel"
        />
      </transition>
      <StudentList
        ref="listRef"
        @edit="openEditForm"
        @toast="handleToastFromList"
      />
    </main>

    <ToastNotification :toasts="toasts" @dismiss="dismissToast" />
  </div>
</template>

<style>
/* === Clean SaaS Design Tokens === */
:root {
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-text: #0f172a;
  --color-text-secondary: #64748b;
  --color-primary: #6366f1;
  --color-primary-hover: #4f46e5;
  --color-primary-light: #eef2ff;
  --color-danger: #ef4444;
  --color-danger-hover: #dc2626;
  --color-border: #e2e8f0;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  --radius: 12px;
}

/* === Reset & Base === */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}

/* === App Shell === */
.app-shell {
  max-width: 1024px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

/* === Header === */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  font-size: 2rem;
  line-height: 1;
}

.app-header h1 {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.825rem;
  color: var(--color-text-secondary);
  margin-top: 0.1rem;
}

/* === Main Container === */
.app-main {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

/* === Shared Button Hierarchy === */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
  line-height: 1.4;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: #ffffff;
  border-color: var(--color-primary);
  box-shadow: 0 1px 2px rgba(99, 102, 241, 0.2);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-add {
  padding: 0.55rem 1.15rem;
  font-size: 0.875rem;
}

.btn-icon {
  font-size: 1.05rem;
  font-weight: 700;
}

.btn-outline {
  background: var(--color-surface);
  color: var(--color-text);
  border-color: var(--color-border);
}

.btn-outline:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}

.btn-ghost:hover:not(:disabled) {
  background: #f1f5f9;
  color: var(--color-text);
}

.btn-danger {
  background: var(--color-surface);
  color: var(--color-danger);
  border-color: #fecaca;
}

.btn-danger:hover:not(:disabled) {
  background: #fef2f2;
  border-color: var(--color-danger);
}

.btn-small {
  padding: 0.3rem 0.6rem;
  font-size: 0.775rem;
}

/* === Transitions === */
.slide-fade-enter-active { transition: all 0.25s ease-out; }
.slide-fade-leave-active { transition: all 0.2s ease-in; }
.slide-fade-enter-from { opacity: 0; transform: translateY(-8px); }
.slide-fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* === Responsive === */
@media (max-width: 640px) {
  .app-shell { padding: 1rem; }
  .app-main { padding: 1rem; }
  .app-header h1 { font-size: 1.15rem; }
}
</style>
