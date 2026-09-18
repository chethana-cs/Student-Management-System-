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
  <div class="app">
    <header class="app-header">
      <h1>Student Management System</h1>
      <button v-if="!showForm" @click="openCreateForm" class="btn btn-primary">
        + Add Student
      </button>
    </header>

    <main class="app-main">
      <StudentForm
        v-if="showForm"
        :student="editingStudent"
        @saved="onSaved"
        @cancel="onCancel"
      />
      <StudentList ref="listRef" @edit="openEditForm" />
    </main>
  </div>
</template>

<style>
/* === CSS Variables (Design Tokens) === */
:root {
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-primary: #6366f1;
  --color-primary-hover: #4f46e5;
  --color-danger: #ef4444;
  --color-danger-hover: #dc2626;
  --color-border: #e2e8f0;
  --color-row-hover: #f1f5f9;
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
}

/* === Layout === */
.app {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.app-main {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* === Shared Button Styles === */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-secondary {
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-border);
}

.btn-danger {
  background: var(--color-danger);
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: var(--color-danger-hover);
}

.btn-small {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
}
</style>
