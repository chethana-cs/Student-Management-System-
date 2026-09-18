<script setup>
import { ref } from 'vue'
import StudentList from '@/components/StudentList.vue'
import StudentForm from '@/components/StudentForm.vue'

const showForm = ref(false)
const editingStudent = ref(null)
const listRef = ref(null)

function openCreateForm() {
  editingStudent.value = null
  showForm.value = true
}

function openEditForm(student) {
  editingStudent.value = { ...student }
  showForm.value = true
}

function onSaved() {
  showForm.value = false
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
          <p class="header-subtitle">Manage student records efficiently</p>
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
      <StudentList ref="listRef" @edit="openEditForm" />
    </main>
  </div>
</template>

<style>
/* === CSS Variables (Design Tokens) === */
:root {
  --color-bg: #f1f5f9;
  --color-surface: #ffffff;
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-primary: #6366f1;
  --color-primary-hover: #4f46e5;
  --color-primary-light: #eef2ff;
  --color-danger: #ef4444;
  --color-danger-hover: #dc2626;
  --color-border: #e2e8f0;
  --color-row-hover: #f8fafc;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.08);
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
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}

/* === App Shell === */
.app-shell {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
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
  gap: 0.75rem;
}

.logo {
  font-size: 2rem;
  line-height: 1;
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-top: 0.1rem;
}

/* === Main Content Area === */
.app-main {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.75rem;
  box-shadow: var(--shadow-md);
}

/* === Shared Button Styles === */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.55rem 1.1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  line-height: 1.4;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary), #818cf8);
  color: #fff;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-hover), #6366f1);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  transform: translateY(-1px);
}

.btn-add {
  padding: 0.6rem 1.25rem;
  font-size: 0.9rem;
}

.btn-icon {
  font-size: 1.1rem;
  font-weight: 700;
}

.btn-outline {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1.5px solid var(--color-border);
}

.btn-outline:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1.5px solid var(--color-border);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--color-bg);
  color: var(--color-text);
}

.btn-danger {
  background: var(--color-surface);
  color: var(--color-danger);
  border: 1.5px solid #fecaca;
}

.btn-danger:hover:not(:disabled) {
  background: #fef2f2;
  border-color: var(--color-danger);
}

.btn-small {
  padding: 0.35rem 0.65rem;
  font-size: 0.8rem;
}

/* === Transitions === */
.slide-fade-enter-active {
  transition: all 0.25s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* === Responsive === */
@media (max-width: 600px) {
  .app-shell {
    padding: 1rem;
  }

  .app-header h1 {
    font-size: 1.2rem;
  }

  .app-main {
    padding: 1rem;
  }
}
</style>
