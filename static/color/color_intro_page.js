// static/color/color_intro.js

/**
 * Manages intro screens for color tests
 */
export class ColorIntro {
  constructor(container) {
    this.container = container;
    this.introElement = null;
  }

  /**
   * Show intro screen
   * @param {Object} config
   * @param {string} config.title
   * @param {string} config.description
   * @param {string[]} [config.instructions]
   * @param {Function} config.onStart
   * @param {string} [config.estimatedTime]
   */
  show({ title, description, instructions = [], onStart, estimatedTime }) {
    this.hide();

    this.container.innerHTML = `
      <h2 class="card-title" id="helpTitle">${title}</h2>
      <p class="card-body">${description}</p>
      ${instructions.length ? this._renderInstructions(instructions) : ''}
      ${estimatedTime ? `<p class="caption">⏱️ Estimated time: ${estimatedTime}</p>` : ''}
      <div class="actions actions-center">
        <button class="btn btn-primary" id="startButton">Start Test</button>
      </div>
    `;

    const startBtn = this.introElement.querySelector('#startButton');
    startBtn.addEventListener('click', () => {
      this.hide();
      onStart();
    });
  }

  _renderInstructions(instructions) {
    return `
      <ul>
        ${instructions.map(item => `<li>${item}</li>`).join('')}
      </ul>
    `;
  }

  hide() {
    if (this.introElement) {
      this.introElement.remove();
      this.introElement = null;
    }
  }

  isShowing() {
    return this.introElement !== null;
  }
}
