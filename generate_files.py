// 注意: quizData と categoryList は data.js から読み込まれます

const labels = ["(ア)", "(イ)", "(ウ)", "(エ)"];

const app = {
    mode: 'list', // 'list' or 'quiz'
    category: 'all',
    currentQuizIndex: 0,
    filteredQuestions: [],
    wrongQuestions: [],

    init: function() {
        // 1. カテゴリメニューを data.js の内容から自動生成
        this.generateCategoryMenu();

        // 2. 最初のカテゴリを選択
        this.selectCategory('all');
    },

    // カテゴリメニューの自動生成（ソート機能を追加）
    generateCategoryMenu: function() {
        const select = document.getElementById('category-select');
        select.innerHTML = ''; // 一旦空にする

        // 「すべて」の選択肢を追加
        const allOpt = document.createElement('option');
        allOpt.value = 'all';
        allOpt.text = '📚 すべての問題';
        select.appendChild(allOpt);

        // キーを取得して明示的に並び替え
        const keys = Object.keys(categoryList).sort();

        // 並び替えたキー順に選択肢を追加
        keys.forEach(key => {
            const opt = document.createElement('option');
            opt.value = key;
            opt.text = categoryList[key];
            select.appendChild(opt);
        });
    },

    setMode: function(mode) {
        this.mode = mode;
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(`mode-${mode}`).classList.add('active');
        this.resetQuizData();
        this.render();
    },

    selectCategory: function(cat) {
        this.category = cat;
        this.resetQuizData();
        this.render();
    },

    resetQuizData: function(customList = null) {
        this.currentQuizIndex = 0;
        this.wrongQuestions = [];

        if (customList) {
            this.filteredQuestions = [...customList];
            this.shuffle(this.filteredQuestions);
            return;
        }

        let baseList = [];
        if (this.category === 'all') {
            baseList = [...quizData];
        } else {
            baseList = quizData.filter(q => q.cat === this.category);
        }

        if (this.mode === 'quiz') {
            this.shuffle(baseList);
        }

        this.filteredQuestions = baseList;
    },

    shuffle: function(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    },

    render: function() {
        const container = document.getElementById('main-content');
        container.innerHTML = '';
        window.scrollTo(0,0);

        if (this.filteredQuestions.length === 0) {
            container.innerHTML = '<p style="text-align:center;">このカテゴリに問題はありません。</p>';
            return;
        }

        if (this.mode === 'list') {
            this.renderListView(container);
        } else {
            this.renderQuizView(container);
        }
    },

    renderListView: function(container) {
        this.filteredQuestions.forEach((q, i) => {
            const card = document.createElement('div');
            card.className = 'question-card';

            const optsHtml = q.opts.map((o, idx) =>
                `<li class="option-item">${labels[idx]} ${o}</li>`
            ).join('');

            card.innerHTML = `
                <div class="q-header"><span>No. ${i + 1}</span> <span>ID: ${q.id}</span></div>
                <div class="q-text">${q.q}</div>
                <ul class="option-list">${optsHtml}</ul>
                <details>
                    <summary>答えを見る</summary>
                    <div class="ans-text">正解: ${labels[q.ans]} ${q.opts[q.ans]}</div>
                </details>
            `;
            container.appendChild(card);
        });
    },

    renderQuizView: function(container) {
        const q = this.filteredQuestions[this.currentQuizIndex];
        const total = this.filteredQuestions.length;

        const card = document.createElement('div');
        card.className = 'question-card';
        card.innerHTML = `
            <div class="q-header">
                <span>問題 ${this.currentQuizIndex + 1} / ${total}</span>
                <span>Category: ${q.cat}</span>
            </div>
            <div class="q-text">${q.q}</div>
            <div id="quiz-options"></div>
            <div id="result-msg" class="result-msg"></div>
            <div class="quiz-nav">
                <button class="btn btn-secondary" onclick="app.prevQuiz()" ${this.currentQuizIndex === 0 ? 'disabled' : ''}>前へ</button>
                <button id="btn-next" class="btn btn-next" onclick="app.nextQuiz()" disabled>次へ</button>
            </div>
        `;
        container.appendChild(card);

        const optsContainer = card.querySelector('#quiz-options');
        q.opts.forEach((opt, idx) => {
            const btn = document.createElement('button');
            btn.className = 'quiz-option';
            btn.textContent = `${labels[idx]} ${opt}`;
            btn.onclick = () => this.checkAnswer(btn, idx, q.ans, q);
            optsContainer.appendChild(btn);
        });
    },

    checkAnswer: function(btn, selectedIdx, correctIdx, questionObj) {
        if (document.querySelector('.quiz-option.correct') || document.querySelector('.quiz-option.wrong')) return;

        const opts = document.querySelectorAll('.quiz-option');
        const msg = document.getElementById('result-msg');

        if (selectedIdx === correctIdx) {
            btn.classList.add('correct');
            msg.textContent = "🙆‍♂️ 正解！";
            msg.style.display = "block";
            msg.style.backgroundColor = "#dcfce7";
            msg.style.color = "#166534";
        } else {
            btn.classList.add('wrong');
            opts[correctIdx].classList.add('correct');
            msg.textContent = "🙅‍♀️ 不正解...";
            msg.style.display = "block";
            msg.style.backgroundColor = "#fee2e2";
            msg.style.color = "#991b1b";
            this.wrongQuestions.push(questionObj);
        }

        document.getElementById('btn-next').disabled = false;
    },

    nextQuiz: function() {
        if (this.currentQuizIndex < this.filteredQuestions.length - 1) {
            this.currentQuizIndex++;
            this.render();
        } else {
            this.renderResultView();
        }
    },

    prevQuiz: function() {
        if (this.currentQuizIndex > 0) {
            this.currentQuizIndex--;
            this.render();
        }
    },

    renderResultView: function() {
        const container = document.getElementById('main-content');
        const total = this.filteredQuestions.length;
        const wrongCount = this.wrongQuestions.length;
        const correctCount = total - wrongCount;

        let msg = "";
        if (correctCount === total) msg = "素晴らしい！全問正解です🎉";
        else if (correctCount >= total * 0.8) msg = "おしい！あと少し！👍";
        else msg = "復習して再チャレンジしましょう💪";

        const retryWrongBtn = wrongCount > 0
            ? `<button class="btn btn-retry-wrong" onclick="app.retryWrong()">🔄 間違えた問題のみ (${wrongCount}問)</button>`
            : '';

        container.innerHTML = `
            <div class="question-card result-container">
                <h2>テスト終了！</h2>
                <div class="score-text">${correctCount} / ${total} 問 正解</div>
                <p>${msg}</p>
                <div class="result-actions">
                    <button class="btn btn-retry-all" onclick="app.retryAll()">🔄 もう一度 (全問ランダム)</button>
                    ${retryWrongBtn}
                    <button class="btn btn-home" onclick="app.selectCategory('all'); app.setMode('list');">🏠 一覧に戻る</button>
                </div>
            </div>
        `;
    },

    retryAll: function() {
        this.resetQuizData();
        this.render();
    },

    retryWrong: function() {
        const wrongs = [...this.wrongQuestions];
        this.resetQuizData(wrongs);
        this.render();
    }
};

window.onload = function() {
    app.init();
};
