class DynamicBackgroundScene {
  constructor(root, canvas, controls) {
    this.root = root;
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d", { alpha: true, desynchronized: true });
    this.controls = controls;

    this.combo = 0;
    this.state = 1;
    this.thresholds = {
      1: 0,
      2: 50,
      3: 100,
      4: 150,
    };

    this.logicalWidth = 0;
    this.logicalHeight = 0;
    this.pixelRatio = 1;
    this.frameHandle = 0;
    this.lastFrame = 0;
    this.spawnBudget = 0;
    this.particles = [];
    this.visible = !document.hidden;
    this.reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.reducedMotionQuery.matches;

    this.boundAnimate = this.animate.bind(this);
    this.boundResize = this.resize.bind(this);
    this.boundVisibility = this.handleVisibilityChange.bind(this);
    this.boundMotionChange = this.handleMotionChange.bind(this);

    this.bindControls();
    this.bindSystemEvents();
    this.resize();
    this.setCombo(0);
    this.emitBurst(Math.round(this.getParticleProfile().target * 0.58));
    this.primeParticles(24);

    if (this.visible) {
      this.frameHandle = window.requestAnimationFrame(this.boundAnimate);
    }
  }

  bindControls() {
    const { comboRange, comboValue, stateValue, stateButtons } = this.controls;

    comboRange.addEventListener("input", () => {
      this.setCombo(Number(comboRange.value));
    });

    stateButtons.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-state-target]");
      if (!button) {
        return;
      }

      const state = Number(button.dataset.stateTarget);
      this.setCombo(this.thresholds[state]);
    });

    this.comboValue = comboValue;
    this.stateValue = stateValue;
    this.stateButtons = Array.from(stateButtons.querySelectorAll("button[data-state-target]"));
  }

  bindSystemEvents() {
    window.addEventListener("resize", this.boundResize, { passive: true });
    document.addEventListener("visibilitychange", this.boundVisibility);

    if (typeof this.reducedMotionQuery.addEventListener === "function") {
      this.reducedMotionQuery.addEventListener("change", this.boundMotionChange);
    } else if (typeof this.reducedMotionQuery.addListener === "function") {
      this.reducedMotionQuery.addListener(this.boundMotionChange);
    }
  }

  handleMotionChange(event) {
    this.reducedMotion = event.matches;
  }

  handleVisibilityChange() {
    this.visible = !document.hidden;

    if (!this.visible) {
      this.lastFrame = 0;
      if (this.frameHandle) {
        window.cancelAnimationFrame(this.frameHandle);
        this.frameHandle = 0;
      }
      return;
    }

    if (!this.frameHandle) {
      this.frameHandle = window.requestAnimationFrame(this.boundAnimate);
    }
  }

  resize() {
    const bounds = this.root.getBoundingClientRect();
    this.logicalWidth = Math.max(1, bounds.width);
    this.logicalHeight = Math.max(1, bounds.height);
    this.pixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);

    this.canvas.width = Math.round(this.logicalWidth * this.pixelRatio);
    this.canvas.height = Math.round(this.logicalHeight * this.pixelRatio);
    this.canvas.style.width = `${this.logicalWidth}px`;
    this.canvas.style.height = `${this.logicalHeight}px`;

    this.ctx.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
  }

  getStateFromCombo(combo) {
    if (combo >= this.thresholds[4]) {
      return 4;
    }

    if (combo >= this.thresholds[3]) {
      return 3;
    }

    if (combo >= this.thresholds[2]) {
      return 2;
    }

    return 1;
  }

  getParticleProfile() {
    const base = [
      { target: 56, speedMin: 60, speedMax: 148, sizeMin: 1.4, sizeMax: 3.2 },
      { target: 72, speedMin: 72, speedMax: 172, sizeMin: 1.5, sizeMax: 3.6 },
      { target: 90, speedMin: 84, speedMax: 194, sizeMin: 1.6, sizeMax: 4.0 },
      { target: 108, speedMin: 98, speedMax: 220, sizeMin: 1.8, sizeMax: 4.4 },
    ][this.state - 1];

    if (!this.reducedMotion) {
      return base;
    }

    return {
      target: Math.max(22, Math.round(base.target * 0.52)),
      speedMin: base.speedMin * 0.72,
      speedMax: base.speedMax * 0.72,
      sizeMin: base.sizeMin,
      sizeMax: base.sizeMax,
    };
  }

  setCombo(combo) {
    const nextCombo = Math.max(0, Math.min(999, Math.round(combo)));
    const nextState = this.getStateFromCombo(nextCombo);
    const stateChanged = nextState !== this.state;

    this.combo = nextCombo;
    this.state = nextState;

    this.root.dataset.state = String(nextState);
    this.controls.comboRange.value = String(nextCombo);
    this.comboValue.textContent = String(nextCombo);
    this.stateValue.textContent = String(nextState);

    this.stateButtons.forEach((button) => {
      button.classList.toggle("is-active", Number(button.dataset.stateTarget) === nextState);
    });

    if (stateChanged) {
      this.emitBurst(Math.round(this.getParticleProfile().target * 0.38));
    }
  }

  setState(state) {
    const nextState = Math.max(1, Math.min(4, Math.round(state)));
    this.setCombo(this.thresholds[nextState]);
  }

  spawnParticle(profile) {
    const originX = this.logicalWidth * 0.5 + (Math.random() - 0.5) * 14;
    const originY = this.logicalHeight * 0.5 + (Math.random() - 0.5) * 14;
    const angle = Math.random() * Math.PI * 2;
    const speed = profile.speedMin + Math.random() * (profile.speedMax - profile.speedMin);
    const acceleration = 18 + Math.random() * 26;

    this.particles.push({
      x: originX,
      y: originY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      ax: Math.cos(angle) * acceleration,
      ay: Math.sin(angle) * acceleration,
      life: 0,
      maxLife: 1.5 + Math.random() * 1.5,
      size: profile.sizeMin + Math.random() * (profile.sizeMax - profile.sizeMin),
      flicker: 0.8 + Math.random() * 1.3,
    });
  }

  emitBurst(count) {
    const profile = this.getParticleProfile();
    const burstCount = Math.min(profile.target, Math.max(0, count));

    for (let index = 0; index < burstCount; index += 1) {
      this.spawnParticle(profile);
    }
  }

  primeParticles(frameCount) {
    for (let index = 0; index < frameCount; index += 1) {
      this.updateParticles(1 / 60);
    }
  }

  updateParticles(deltaTime) {
    const profile = this.getParticleProfile();
    const emissionRate = profile.target / 1.05;

    this.spawnBudget += emissionRate * deltaTime;
    while (this.spawnBudget >= 1 && this.particles.length < profile.target) {
      this.spawnParticle(profile);
      this.spawnBudget -= 1;
    }

    this.ctx.clearRect(0, 0, this.logicalWidth, this.logicalHeight);
    this.ctx.globalCompositeOperation = "lighter";

    for (let index = this.particles.length - 1; index >= 0; index -= 1) {
      const particle = this.particles[index];
      particle.life += deltaTime;

      if (particle.life >= particle.maxLife) {
        this.particles.splice(index, 1);
        continue;
      }

      particle.vx += particle.ax * deltaTime;
      particle.vy += particle.ay * deltaTime;
      particle.x += particle.vx * deltaTime;
      particle.y += particle.vy * deltaTime;

      const progress = particle.life / particle.maxLife;
      const alpha = (1 - progress) * (0.96 + Math.sin(particle.life * 10 * particle.flicker) * 0.22);
      const haloAlpha = Math.max(0, alpha * 0.32);
      const coreAlpha = Math.max(0.24, alpha);
      const haloSize = particle.size + progress * 7.2;
      const coreSize = particle.size + progress * 1.6;

      this.ctx.fillStyle = `rgba(255, 255, 255, ${haloAlpha})`;
      this.ctx.beginPath();
      this.ctx.arc(
        particle.x,
        particle.y,
        haloSize,
        0,
        Math.PI * 2
      );
      this.ctx.fill();

      this.ctx.fillStyle = `rgba(255, 255, 255, ${coreAlpha})`;
      this.ctx.beginPath();
      this.ctx.arc(
        particle.x,
        particle.y,
        coreSize,
        0,
        Math.PI * 2
      );
      this.ctx.fill();
    }

    this.ctx.globalCompositeOperation = "source-over";
  }

  animate(timestamp) {
    if (!this.visible) {
      this.frameHandle = 0;
      return;
    }

    if (!this.lastFrame) {
      this.lastFrame = timestamp;
    }

    const deltaTime = Math.min(0.033, (timestamp - this.lastFrame) / 1000);
    this.lastFrame = timestamp;

    this.updateParticles(deltaTime);
    this.frameHandle = window.requestAnimationFrame(this.boundAnimate);
  }

  destroy() {
    if (this.frameHandle) {
      window.cancelAnimationFrame(this.frameHandle);
    }

    window.removeEventListener("resize", this.boundResize);
    document.removeEventListener("visibilitychange", this.boundVisibility);

    if (typeof this.reducedMotionQuery.removeEventListener === "function") {
      this.reducedMotionQuery.removeEventListener("change", this.boundMotionChange);
    } else if (typeof this.reducedMotionQuery.removeListener === "function") {
      this.reducedMotionQuery.removeListener(this.boundMotionChange);
    }
  }
}

const root = document.getElementById("scene");
const canvas = document.getElementById("particles");

const dynamicScene = new DynamicBackgroundScene(root, canvas, {
  comboRange: document.getElementById("comboRange"),
  comboValue: document.getElementById("comboValue"),
  stateValue: document.getElementById("stateValue"),
  stateButtons: document.getElementById("stateButtons"),
});

const searchParams = new URLSearchParams(window.location.search);
document.body.classList.toggle("debug-open", searchParams.get("debug") === "1");

window.addEventListener("keydown", (event) => {
  const activeTag = document.activeElement?.tagName;
  if (activeTag === "INPUT" || activeTag === "TEXTAREA") {
    return;
  }

  if (event.key.toLowerCase() === "d" && !event.ctrlKey && !event.metaKey && !event.altKey) {
    document.body.classList.toggle("debug-open");
  }
});

if (searchParams.has("combo")) {
  dynamicScene.setCombo(Number(searchParams.get("combo")));
} else if (searchParams.has("state")) {
  dynamicScene.setState(Number(searchParams.get("state")));
}

window.dynamicGameScene = {
  setCombo(combo) {
    dynamicScene.setCombo(combo);
  },
  setState(state) {
    dynamicScene.setState(state);
  },
  getState() {
    return dynamicScene.state;
  },
  destroy() {
    dynamicScene.destroy();
  },
};
