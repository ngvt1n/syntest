// ============================================================
// SYNTEST — Shared Utilities + WheelRenderer
// ------------------------------------------------------------
// What this file does:
//   1) Small, pure helpers: clamp, rgbToHex, shuffle
//   2) WheelRenderer: draws an HSL-based color wheel and reports
//      picked colors via an onSelect(r,g,b,hex) callback.
//
// Notes:
//   - DPR-correct rendering/sampling ensures the picked color matches
//     what the user sees on HiDPI screens.
//   - All listeners are cleaned up in destroy() to prevent leaks.
// ============================================================

/** Clamp a value to [min, max]. Pure. */
export const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

/** Convert RGB(0..255) to #RRGGBB. Pure. */
export const rgbToHex = (r, g, b) =>
  [r, g, b]
    .map(n => clamp(n, 0, 255).toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();

/** Fisher–Yates shuffle. Mutates and returns the same array. Pure. */
export const shuffle = arr => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

/** Default visual + behavior options for the wheel. */
const defaultWheelOpts = Object.freeze({
  outlineColor: "#000",
  outlineWidth: 2,
  freezeBorderColor: "#f00",  // dot border when frozen
  liveBorderColor: "#000",    // dot border when movable
  saturation: 1.0,            // fixed S in HSL -> RGB
  // The dot is a positioned element the page provides (for accessibility/visibility)
  dotRadius: 7                // used only to position the dot aesthetically
});

/**
 * WheelRenderer
 * Draws an HSL wheel (H on X, L on Y, constant S) and lets the user pick colors.
 * Emits the selection via `onSelect({ r, g, b, hex })`.
 *
 * @param {HTMLCanvasElement} canvas  The visible canvas to draw into
 * @param {HTMLElement}       dot     Absolutely-positioned marker shown at pick point
 * @param {(sel: {r:number,g:number,b:number,hex:string})=>void} onSelect  Callback for selections
 * @param {Partial<typeof defaultWheelOpts>} [opts]  Optional visual behavior overrides
 */
export class WheelRenderer {
  constructor(canvas, dot, onSelect, opts = {}) {
    // ---- Save collaborators
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d", { willReadFrequently: true });
    this.dot = dot;
    this.onSelect = onSelect;
    this.opts = { ...defaultWheelOpts, ...opts };

    // ---- State
    this.isDragging = false;
    this.isFrozen = false;

    // ---- Backing store sizing to honor devicePixelRatio (DPR)
    // So what you see equals what we sample.
    this._setupDPR();

    // ---- Draw once and wire the events
    this._draw();
    this._drawOutline();
    this._wireEvents();
  }

  // ===========================
  // Canvas setup & drawing
  // ===========================
  _setupDPR() {
    const dpr = window.devicePixelRatio || 1;
    // CSS pixels
    const cssSize = this.canvas.width; // author sets width=height in HTML/JS
    // Backing pixels
    this.canvas.width = Math.floor(cssSize * dpr);
    this.canvas.height = Math.floor(cssSize * dpr);
    // Scale context so drawing math can still use CSS pixels
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.size = cssSize; // logical drawing size in CSS pixels
  }

  _draw() {
    const { ctx, size } = this;
    const img = ctx.createImageData(size, size);
    const data = img.data;

    // HSL plane: H = x/size * 360, L = 1 - y/size, S = fixed
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const idx = (y * size + x) * 4;
        const h = (x / size) * 360;
        const l = 1 - y / size;
        const s = this.opts.saturation;
        const [r, g, b] = this._hslToRgb(h, s, l);
        data[idx]     = r;
        data[idx + 1] = g;
        data[idx + 2] = b;
        data[idx + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
  }

  _drawOutline() {
    const { ctx, size } = this;
    ctx.lineWidth = this.opts.outlineWidth;
    ctx.strokeStyle = this.opts.outlineColor;
    // 0.5 offset keeps the hairline crisp
    ctx.strokeRect(0.5, 0.5, size - 1, size - 1);
  }

  /** HSL(0..360, 0..1, 0..1) -> RGB(0..255). Pure. */
  _hslToRgb(h, s, l) {
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = l - c / 2;
    let r = 0, g = 0, b = 0;

    if (h < 60)      [r, g, b] = [c, x, 0];
    else if (h < 120)[r, g, b] = [x, c, 0];
    else if (h < 180)[r, g, b] = [0, c, x];
    else if (h < 240)[r, g, b] = [0, x, c];
    else if (h < 300)[r, g, b] = [x, 0, c];
    else             [r, g, b] = [c, 0, x];

    return [
      Math.round((r + m) * 255),
      Math.round((g + m) * 255),
      Math.round((b + m) * 255)
    ];
  }

  // ===========================
  // Events & interaction
  // ===========================
  _wireEvents() {
    // Save bound handlers so we can remove them in destroy()
    this._onMouseDown = (e) => {
      if (this.isFrozen) return;
      this.isDragging = true;
      const s = this._sampleAtEvent(e);
      if (s) this.onSelect?.(s);
    };

    this._onMouseMove = (e) => {
      if (!this.isDragging || this.isFrozen) return;
      const s = this._sampleAtEvent(e);
      if (s) this.onSelect?.(s);
    };

    this._onMouseUp = () => { this.isDragging = false; };

    this._onClick = (e) => {
      const s = this._sampleAtEvent(e);
      if (!s) return;

      // Toggle freeze; when frozen, dot border shows "locked" state
      this.isFrozen = !this.isFrozen;
      if (this.dot) {
        this.dot.style.borderColor = this.isFrozen
          ? this.opts.freezeBorderColor
          : this.opts.liveBorderColor;
      }
      if (!this.isFrozen) {
        // When unfreezing via click, also re-emit selection so UI is in sync
        this.onSelect?.(s);
      }
    };

    this.canvas.addEventListener("mousedown", this._onMouseDown);
    this.canvas.addEventListener("mousemove", this._onMouseMove);
    window.addEventListener("mouseup", this._onMouseUp);
    this.canvas.addEventListener("click", this._onClick);
  }

  /**
   * Convert a mouse event to canvas coords, sample the pixel, move the dot,
   * and return the selected color.
   */
  _sampleAtEvent(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = Math.floor(e.clientX - rect.left);
    const y = Math.floor(e.clientY - rect.top);

    if (x < 0 || x >= this.size || y < 0 || y >= this.size) return null;

    // Read from the *display* canvas (DPR already handled by setTransform)
    const p = this.ctx.getImageData(x, y, 1, 1).data;

    if (this.dot) {
      this.dot.style.display = "block";
      // Slight offset so the dot is centered on the cursor
      const r = this.opts.dotRadius;
      this.dot.style.left = `${x - r}px`;
      this.dot.style.top  = `${y - r}px`;
    }

    return { r: p[0], g: p[1], b: p[2], hex: rgbToHex(p[0], p[1], p[2]) };
  }

  // ===========================
  // Lifecycle helpers
  // ===========================

  /** Public: programmatically freeze/unfreeze the wheel. */
  setFrozen(frozen) {
    this.isFrozen = !!frozen;
    if (this.dot) {
      this.dot.style.borderColor = this.isFrozen
        ? this.opts.freezeBorderColor
        : this.opts.liveBorderColor;
    }
  }

  /** Public: remove listeners if you tear down the UI. */
  destroy() {
    this.canvas.removeEventListener("mousedown", this._onMouseDown);
    this.canvas.removeEventListener("mousemove", this._onMouseMove);
    window.removeEventListener("mouseup", this._onMouseUp);
    this.canvas.removeEventListener("click", this._onClick);
  }
}
