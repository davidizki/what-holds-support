document.documentElement.classList.add("js");

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const progressBar = document.querySelector(".scroll-progress span");

function updateScrollProgress() {
  if (!progressBar) return;
  const available = document.documentElement.scrollHeight - window.innerHeight;
  const progress = available > 0 ? Math.min(1, window.scrollY / available) : 0;
  progressBar.style.transform = `scaleX(${progress})`;
}

let scrollFrame = 0;
window.addEventListener("scroll", () => {
  if (scrollFrame) return;
  scrollFrame = window.requestAnimationFrame(() => {
    updateScrollProgress();
    scrollFrame = 0;
  });
}, { passive: true });
updateScrollProgress();

const reveals = Array.from(document.querySelectorAll(".reveal"));
if (reducedMotion.matches || !("IntersectionObserver" in window)) {
  reveals.forEach((element) => element.classList.add("is-visible"));
} else {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -9%", threshold: 0.12 });
  reveals.forEach((element) => revealObserver.observe(element));
}

const knowledgeStage = document.querySelector(".knowledge-stage");
if (knowledgeStage && !reducedMotion.matches && window.matchMedia("(pointer: fine)").matches) {
  knowledgeStage.addEventListener("pointermove", (event) => {
    const bounds = knowledgeStage.getBoundingClientRect();
    const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 16;
    const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * 16;
    knowledgeStage.style.setProperty("--stage-x", `${x}px`);
    knowledgeStage.style.setProperty("--stage-y", `${y}px`);
  });
  knowledgeStage.addEventListener("pointerleave", () => {
    knowledgeStage.style.setProperty("--stage-x", "0px");
    knowledgeStage.style.setProperty("--stage-y", "0px");
  });
}

function activateTabs(buttons, activate) {
  buttons.forEach((button, index) => {
    button.addEventListener("click", () => activate(button));
    button.addEventListener("keydown", (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = buttons.length - 1;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % buttons.length;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + buttons.length) % buttons.length;
      buttons[next].focus();
      activate(buttons[next]);
    });
  });
}

const scienceButtons = Array.from(document.querySelectorAll("[data-science-target]"));
const scienceConsole = document.querySelector(".science-console");
function activateScience(selected) {
  const target = selected.dataset.scienceTarget;
  scienceButtons.forEach((button) => {
    button.setAttribute("aria-selected", String(button === selected));
    button.tabIndex = button === selected ? 0 : -1;
  });
  document.querySelectorAll("[data-science-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.sciencePanel !== target;
  });
  document.querySelectorAll("[data-science-scene]").forEach((scene) => {
    scene.hidden = scene.dataset.scienceScene !== target;
  });
  if (scienceConsole) scienceConsole.dataset.activeScience = target;
}
activateTabs(scienceButtons, activateScience);
if (scienceButtons.length) activateScience(scienceButtons.find((button) => button.getAttribute("aria-selected") === "true") || scienceButtons[0]);

const demoButtons = Array.from(document.querySelectorAll("[data-demo-target]"));
function activateDemo(selected) {
  const target = selected.dataset.demoTarget;
  demoButtons.forEach((button) => {
    button.setAttribute("aria-selected", String(button === selected));
    button.tabIndex = button === selected ? 0 : -1;
  });
  document.querySelectorAll("[data-demo-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.demoPanel !== target;
  });
  document.querySelectorAll("[data-demo-copy]").forEach((panel) => {
    panel.hidden = panel.dataset.demoCopy !== target;
  });
}
activateTabs(demoButtons, activateDemo);
if (demoButtons.length) activateDemo(demoButtons.find((button) => button.getAttribute("aria-selected") === "true") || demoButtons[0]);
