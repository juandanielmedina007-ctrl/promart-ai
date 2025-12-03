document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    const resultContainer = document.getElementById('resultContainer');
    const clarificationContainer = document.getElementById('clarificationContainer');
    const loadingMessages = document.getElementById('loadingMessages');
    const loadingTitle = document.getElementById('loadingTitle');
    const loadingSubtitle = document.getElementById('loadingSubtitle');
    const questionsList = document.getElementById('questionsList');
    const sendAnswersBtn = document.getElementById('sendAnswersBtn');
    const loader = document.querySelector('.loader');
    const btnText = document.querySelector('.btn-text');

    // Elements to update in result
    const recTitle = document.getElementById('recTitle');
    const recAnalysis = document.getElementById('recAnalysis');
    const cardsGrid = document.getElementById('cardsGrid');

    let currentQuery = "";
    let loadingInterval;

    const loadingSteps = [
        { title: "🔍 Buscando las mejores opciones...", subtitle: "Navegando a Promart" },
        { title: "📦 Analizando productos...", subtitle: "Extrayendo información de precios y características" },
        { title: "🧠 Consultando a la IA...", subtitle: "Seleccionando las mejores opciones para ti" },
        { title: "✨ Preparando resultados...", subtitle: "Casi listo..." }
    ];

    searchBtn.addEventListener('click', () => performSearch());
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    sendAnswersBtn.addEventListener('click', submitAnswers);

    async function performSearch(answers = null) {
        const query = searchInput.value.trim();
        if (!query) return;

        currentQuery = query;

        // UI Loading State
        setLoading(true);
        resultContainer.classList.add('hidden');
        clarificationContainer.classList.add('hidden');
        showLoadingMessages();

        try {
            const payload = { query: query };
            if (answers) {
                payload.answers = answers;
            }

            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            hideLoadingMessages();

            if (data.type === 'clarification') {
                renderClarification(data.questions);
            } else if (data.type === 'result') {
                renderResults(data);
            } else if (data.type === 'error') {
                alert(data.message);
            }

        } catch (error) {
            console.error('Error:', error);
            hideLoadingMessages();
            alert('Ocurrió un error al procesar tu solicitud.');
        } finally {
            setLoading(false);
        }
    }

    function showLoadingMessages() {
        loadingMessages.classList.remove('hidden');
        let step = 0;

        // Mostrar primer mensaje
        updateLoadingMessage(step);

        // Cambiar mensajes cada 3 segundos
        loadingInterval = setInterval(() => {
            step++;
            if (step < loadingSteps.length) {
                updateLoadingMessage(step);
            } else {
                clearInterval(loadingInterval);
            }
        }, 3000);
    }

    function updateLoadingMessage(step) {
        loadingTitle.textContent = loadingSteps[step].title;
        loadingSubtitle.textContent = loadingSteps[step].subtitle;
    }

    function hideLoadingMessages() {
        loadingMessages.classList.add('hidden');
        if (loadingInterval) {
            clearInterval(loadingInterval);
        }
    }

    function renderClarification(questions) {
        questionsList.innerHTML = '';
        questions.forEach((q, index) => {
            const div = document.createElement('div');
            div.className = 'question-item';
            div.innerHTML = `
                <label>${q}</label>
                <input type="text" class="answer-input" data-index="${index}" placeholder="Tu respuesta...">
            `;
            questionsList.appendChild(div);
        });
        clarificationContainer.classList.remove('hidden');
    }

    function submitAnswers() {
        const inputs = document.querySelectorAll('.answer-input');
        const answers = [];
        inputs.forEach(input => {
            if (input.value.trim()) answers.push(input.value.trim());
        });

        performSearch(answers);
    }

    function renderResults(data) {
        recTitle.textContent = data.titulo;
        recAnalysis.textContent = data.analisis_general;
        cardsGrid.innerHTML = '';

        data.recomendaciones.forEach(prod => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <div class="card-tag">${prod.etiqueta || 'Recomendado'}</div>
                <img src="${prod.imagen || ''}" alt="${prod.nombre}" class="card-img">
                <div class="card-reason">"${prod.razon}"</div>
                <h3 class="card-title">${prod.nombre}</h3>
                <div class="card-footer">
                    <span class="card-price">${prod.precio}</span>
                    <a href="${prod.link}" target="_blank" class="card-btn">Ver</a>
                </div>
            `;
            cardsGrid.appendChild(card);
        });

        resultContainer.classList.remove('hidden');
    }

    function setLoading(isLoading) {
        searchBtn.disabled = isLoading;
        if (isLoading) {
            loader.classList.remove('hidden');
            btnText.classList.add('hidden');
        } else {
            loader.classList.add('hidden');
            btnText.classList.remove('hidden');
        }
    }
});
