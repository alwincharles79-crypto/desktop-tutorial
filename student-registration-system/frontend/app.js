const $ = (id) => document.getElementById(id);
let editingId = null;
let studentsCache = [];
let toastTimer;

function toast(message) {
  const el = $('toast'); el.textContent = message; el.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 2600);
}
function initials(name) { return name.split(/\s+/).slice(0,2).map(x => x[0]).join('').toUpperCase(); }
function niceDate(value) { return value ? new Date(value.replace(' ', 'T') + (value.includes('Z') ? '' : 'Z')).toLocaleDateString(undefined,{day:'2-digit',month:'short',year:'numeric'}) : '—'; }
async function api(url, options={}) {
  const response = await fetch(url, {headers:{'Content-Type':'application/json',...(options.headers||{})},...options});
  if (!response.ok) { let message = 'Something went wrong.'; try { const data=await response.json(); message=Array.isArray(data.detail)?data.detail.join(' '):data.detail||message; } catch {} throw new Error(message); }
  return response.status === 204 ? null : response.json();
}
function showPage(page) {
  ['dashboard','students','register'].forEach(p => $(p+'-page').classList.toggle('hidden',p!==page));
  document.querySelectorAll('.nav').forEach(b=>b.classList.toggle('active',b.dataset.page===page));
  $('page-title').textContent = page==='dashboard'?'Dashboard':page==='students'?'Student records':'Register student';
  if(page==='dashboard') loadDashboard(); if(page==='students') loadStudents();
}
async function loadDashboard() {
  try {
    const data=await api('/api/stats');
    $('total-students').textContent=data.total_students; $('today-registrations').textContent=data.today_registrations; $('total-courses').textContent=data.total_courses;
    $('recent-list').innerHTML=data.recent.length?data.recent.map(s=>`<div class="recent-row"><div class="avatar">${initials(s.student_name)}</div><div class="recent-info"><strong>${escapeHtml(s.student_name)}</strong><span>${escapeHtml(s.course)}</span></div><span class="recent-date">${niceDate(s.registration_date)}</span></div>`).join(''):'<div class="empty">No registrations yet. Add your first student to get started.</div>';
  } catch(e) { toast(e.message); }
}
function escapeHtml(value) { return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
async function loadStudents() {
  try {
    const q=$('search').value.trim(); studentsCache=await api('/api/students'+(q?'?search='+encodeURIComponent(q):''));
    $('student-table').innerHTML=studentsCache.length?studentsCache.map(s=>`<tr><td>#${s.id}</td><td><strong>${escapeHtml(s.student_name)}</strong></td><td>${escapeHtml(s.email)}</td><td>${escapeHtml(s.phone)}</td><td>${escapeHtml(s.course)}</td><td>${niceDate(s.registration_date)}</td><td><div class="actions"><button class="action-btn" data-edit="${s.id}">Edit</button><button class="action-btn delete" data-delete="${s.id}">Delete</button></div></td></tr>`).join(''):'<tr><td colspan="7" class="empty">No student records found.</td></tr>';
  } catch(e) { toast(e.message); }
}
function openForm(student=null) {
  editingId=student?.id??null; $('student-form').reset(); $('form-error').textContent='';
  $('form-heading').textContent=editingId?'Update student details':'Register a student'; $('submit-button').textContent=editingId?'Save changes':'Save registration';
  if(student) Object.entries({student_name:student.student_name,email:student.email,phone:student.phone,course:student.course}).forEach(([k,v])=>$('student-form').elements[k].value=v);
  showPage('register');
}
$('student-form').addEventListener('submit',async e=>{
  e.preventDefault(); $('form-error').textContent='';
  const payload=Object.fromEntries(new FormData(e.currentTarget).entries());
  try { await api(editingId?`/api/students/${editingId}`:'/api/students',{method:editingId?'PUT':'POST',body:JSON.stringify(payload)}); toast(editingId?'Student details updated.':'Student registered successfully.'); editingId=null; e.currentTarget.reset(); showPage('students'); }
  catch(err) { $('form-error').textContent=err.message; }
});
document.querySelectorAll('.nav').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.page==='register')openForm();else showPage(b.dataset.page);}));
$('top-add').addEventListener('click',()=>openForm()); $('cancel-form').addEventListener('click',()=>showPage('students')); $('view-all').addEventListener('click',()=>showPage('students'));
$('search').addEventListener('input',()=>{clearTimeout(window.searchDelay);window.searchDelay=setTimeout(loadStudents,220);});
$('student-table').addEventListener('click',async e=>{
  const edit=e.target.closest('[data-edit]'), del=e.target.closest('[data-delete]');
  if(edit){const student=studentsCache.find(s=>s.id===Number(edit.dataset.edit));if(student)openForm(student);}
  if(del){const id=Number(del.dataset.delete);if(!confirm('Delete this student record? This action cannot be undone.'))return;try{await api(`/api/students/${id}`,{method:'DELETE'});toast('Student record deleted.');loadStudents();loadDashboard();}catch(err){toast(err.message);}}
});
$('export').addEventListener('click',()=>{window.location.href='/api/export';});
$('today-label').textContent=new Date().toLocaleDateString(undefined,{weekday:'short',day:'numeric',month:'short',year:'numeric'});
showPage('dashboard');
