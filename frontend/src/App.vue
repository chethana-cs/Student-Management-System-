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
        <div class="logo">SM</div>
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
/* === Light workspace design tokens === */
:root {
  --color-bg: #f6f8f5;
  --color-surface: #ffffff;
  --color-text: #1f2937;
  --color-text-secondary: #6b7280;
  --color-primary: #0f766e;
  --color-primary-hover: #0b5f59;
  --color-primary-light: #e9f7f3;
  --color-danger: #dc2626;
  --color-danger-hover: #b91c1c;
  --color-border: #d9e4de;
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 16px 36px -28px rgba(15, 118, 110, 0.28);
  --radius: 16px;
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
  background: radial-gradient(circle at 10% 0%, #e4f4ed 0, transparent 26rem), var(--color-bg);
  color: var(--color-text);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}

/* === App Shell === */
.app-shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 2.75rem 1.5rem 3.5rem;
}

/* === Header === */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.75rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.logo {
  display: grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  font-size: 1.45rem;
  line-height: 1;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #d7e8df;
  box-shadow: var(--shadow-sm);
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-top: 0.1rem;
}

/* === Main Container === */
.app-main {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.75rem;
  box-shadow: var(--shadow-md);
}

/* === Shared Button Hierarchy === */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  border-radius: 9px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s ease, background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
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
  box-shadow: 0 5px 10px -6px rgba(15, 118, 110, 0.62);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn:hover:not(:disabled) { transform: translateY(-1px); }
.btn:focus-visible,
input:focus-visible,
select:focus-visible { outline: 3px solid rgba(15, 118, 110, 0.2); outline-offset: 2px; }

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
  .app-shell { padding: 1.25rem 1rem 2rem; }
  .app-main { padding: 1rem; }
  .app-header h1 { font-size: 1.15rem; }
}
</style>
