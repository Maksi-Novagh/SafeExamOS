/* SafeExamOS offline demonstration: not an examination delivery or grading service.
 * No network access, browser storage, identity or persistent submission.
 */
(function (factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') window.SafeExamDemo = api;
})(function () {
  'use strict';

  const QUESTIONS = Object.freeze([
    Object.freeze({
      title: 'What does HTTPS primarily provide?',
      options: Object.freeze([
        'Encrypted communication with a website',
        'An unlimited Internet connection',
        'Automatic backups of all files'
      ])
    }),
    Object.freeze({
      title: 'Which device normally connects computers within a local Ethernet network?',
      options: Object.freeze([
        'A monitor',
        'A network switch',
        'A keyboard'
      ])
    }),
    Object.freeze({
      title: 'What is a secure response to an unexpected password request?',
      options: Object.freeze([
        'Share the password to avoid delays',
        'Verify the request through a trusted channel',
        'Use the same password on another website'
      ])
    }),
    Object.freeze({
      title: 'Which of these is an operating system?',
      options: Object.freeze([
        'Debian Linux',
        'HDMI',
        'Wi-Fi'
      ])
    })
  ]);

  function createSession() {
    const answers = Array(QUESTIONS.length).fill(null);
    let index = 0;
    let phase = 'questions';
    let receipt = null;

    function requirePhase(expected) {
      if (phase !== expected) throw new Error('Invalid demo session transition');
    }

    function summary() {
      const answered = receipt ? receipt.answered : answers.filter(value => value !== null).length;
      return {answered, total: QUESTIONS.length, unanswered: QUESTIONS.length - answered};
    }

    return {
      get phase() { return phase; },
      get index() { return index; },
      get question() { return QUESTIONS[index]; },
      get answer() { return answers[index]; },
      get questions() { return QUESTIONS; },
      summary,
      select(optionIndex) {
        requirePhase('questions');
        if (!Number.isInteger(optionIndex) || optionIndex < 0 || optionIndex >= QUESTIONS[index].options.length) {
          throw new Error('Invalid option');
        }
        answers[index] = optionIndex;
      },
      move(delta) {
        requirePhase('questions');
        if (delta !== -1 && delta !== 1) throw new Error('Invalid direction');
        const next = index + delta;
        if (next < 0 || next >= QUESTIONS.length) return false;
        index = next;
        return true;
      },
      review() {
        requirePhase('questions');
        phase = 'review';
      },
      resume() {
        requirePhase('review');
        phase = 'questions';
      },
      reviewItems() {
        return QUESTIONS.map((q, i) => ({title: q.title, answered: answers[i] !== null}));
      },
      submit() {
        requirePhase('review');
        receipt = Object.freeze(summary());
        answers.fill(null);
        phase = 'submitted';
        return receipt;
      }
    };
  }

  function mount(doc, host) {
    const model = createSession();
    const get = id => {
      const node = doc.getElementById(id);
      if (!node) throw new Error('Demo UI is missing ' + id);
      return node;
    };

    const questionPane = get('question-panel');
    const reviewPane = get('review-panel');
    const receiptPane = get('receipt-panel');
    const discardPane = get('discard-panel');
    const progress = get('demo-progress');
    const progressText = get('demo-progress-text');
    const questionTitle = get('demo-question');
    const choices = get('demo-options');
    const prev = get('demo-prev');
    const next = get('demo-next');
    const reviewButton = get('demo-review');
    const reviewList = get('demo-review-list');
    const reviewSummary = get('demo-review-summary');
    const receiptText = get('demo-receipt-text');

    function clear(node) {
      while (node.firstChild) node.removeChild(node.firstChild);
    }

    function updateProgress() {
      const counts = model.summary();
      progress.value = counts.answered;
      progress.max = counts.total;
      progressText.textContent = counts.answered + ' of ' + counts.total + ' answered';
    }

    function renderQuestion() {
      const question = model.question;
      questionTitle.textContent = question.title;
      get('demo-question-number').textContent =
        'Question ' + (model.index + 1) + ' of ' + model.questions.length;
      clear(choices);
      question.options.forEach((choice, i) => {
        const label = doc.createElement('label');
        label.className = 'option';
        const radio = doc.createElement('input');
        radio.type = 'radio';
        radio.name = 'demo-answer';
        radio.value = String(i);
        radio.checked = model.answer === i;
        radio.addEventListener('change', () => {
          model.select(i);
          updateProgress();
        });
        const caption = doc.createElement('span');
        caption.textContent = choice;
        label.appendChild(radio);
        label.appendChild(caption);
        choices.appendChild(label);
      });
      prev.disabled = model.index === 0;
      next.disabled = model.index === model.questions.length - 1;
    }

    function renderReview() {
      clear(reviewList);
      model.reviewItems().forEach((item, i) => {
        const li = doc.createElement('li');
        li.textContent = 'Question ' + (i + 1) + ' — ' +
          (item.answered ? 'Answered' : 'Not answered');
        reviewList.appendChild(li);
      });
      const counts = model.summary();
      reviewSummary.textContent = counts.answered + ' answered; ' +
        counts.unanswered + ' unanswered. This only submits to the local demonstration.';
    }

    function render() {
      const phase = model.phase;
      questionPane.hidden = phase !== 'questions';
      reviewPane.hidden = phase !== 'review';
      receiptPane.hidden = phase !== 'submitted';
      discardPane.hidden = true;
      get('demo-phase').textContent =
        phase === 'submitted' ? 'Submitted locally' :
        phase === 'review' ? 'Review answers' : 'Practice in progress';
      updateProgress();
      if (phase === 'questions') renderQuestion();
      if (phase === 'review') renderReview();
      if (phase === 'submitted') {
        const counts = model.summary();
        receiptText.textContent =
          'You submitted ' + counts.answered + ' of ' + counts.total +
          ' answers locally. No answers were uploaded or saved as an exam result.';
      }
    }

    function returnToLauncher() {
      host.SafeExamTransition.request('finish-demo').catch(() => {
        get('demo-phase').textContent = 'Session exit failed';
      });
    }

    prev.addEventListener('click', () => { model.move(-1); render(); });
    next.addEventListener('click', () => { model.move(1); render(); });
    reviewButton.addEventListener('click', () => { model.review(); render(); });
    get('demo-resume').addEventListener('click', () => { model.resume(); render(); });
    get('demo-submit').addEventListener('click', () => { model.submit(); render(); });
    get('demo-done').addEventListener('click', returnToLauncher);
    get('demo-exit').addEventListener('click', () => {
      questionPane.hidden = true;
      reviewPane.hidden = true;
      receiptPane.hidden = true;
      discardPane.hidden = false;
    });
    get('demo-stay').addEventListener('click', render);
    get('demo-discard').addEventListener('click', returnToLauncher);

    render();
    return model;
  }

  return Object.freeze({QUESTIONS, createSession, mount});
});
