let currentIndex = 0;
let books = [];
let openLibraryCover = "";

// ————— SLIDER —————

function getCards() {
    return document.querySelectorAll(".card");
}

function showSlide(index) {
    const cards = getCards();
    cards.forEach(c => c.classList.remove("active"));
    cards[index].classList.add("active");
    updateDots();
}

function nextSlide() {
    const cards = getCards();
    currentIndex = (currentIndex + 1) % cards.length;
    showSlide(currentIndex);
}

function prevSlide() {
    const cards = getCards();
    currentIndex = (currentIndex - 1 + cards.length) % cards.length;
    showSlide(currentIndex);
}

function updateDots() {
    const dots = document.getElementById("dots");
    const cards = getCards();
    const total = cards.length;
    dots.innerHTML = "";

    const visible = 5;
    const half = Math.floor(visible / 2);

    let start = currentIndex - half;
    let end = currentIndex + half;

    if (start < 0) { start = 0; end = Math.min(visible - 1, total - 1); }
    if (end >= total) { end = total - 1; start = Math.max(0, end - visible + 1); }

    for (let i = start; i <= end; i++) {
        const dot = document.createElement("div");
        const distance = Math.abs(i - currentIndex);

        dot.className = "dot" + (i === currentIndex ? " active" : "");
        dot.style.opacity = distance === 0 ? "1" : distance === 1 ? "0.8" : "0.7";
        dot.style.transform = `scale(${distance === 0 ? 1 : distance === 1 ? 0.9 : 0.75})`;
        dot.onclick = () => { currentIndex = i; showSlide(i); };
        dots.appendChild(dot);
    }
}

// ————— FORMULÁRIO —————

function toggleForm(e) {
    if (e) e.stopPropagation();
    const addFace = document.getElementById("add-face");
    const formFace = document.getElementById("form-face");
    addFace.classList.toggle("hidden");
    formFace.classList.toggle("hidden");
}

document.getElementById("add-card").addEventListener("click", function(e) {
    const formFace = document.getElementById("form-face");
    if (!formFace.classList.contains("hidden")) return;
    toggleForm();
});

function previewImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
        const img = document.getElementById("img-preview");
        img.src = e.target.result;
        img.classList.add("visible");
        document.querySelector("#img-label i").style.display = "none";
        document.querySelector("#img-label span").style.display = "none";
    };
    reader.readAsDataURL(file);
}

function setRating(value) {
    document.getElementById("f-rating").value = value;
    const stars = document.querySelectorAll("#stars-input span");
    stars.forEach((s, i) => {
        s.classList.toggle("active", i < value);
    });
}

// ————— BUSCA OPEN LIBRARY —————

async function searchBook() {
    const title = document.getElementById("f-title").value.trim();
    if (!title) return alert("Digite o título do livro!");

    const res = await fetch(`/books/search?q=${encodeURIComponent(title)}`);
    if (!res.ok) return alert("Livro não encontrado na Open Library.");

    const results = await res.json();

    const dropdown = document.getElementById("search-dropdown");
    dropdown.innerHTML = "";

    results.forEach(book => {
        const item = document.createElement("div");
        item.className = "dropdown-item";
        item.innerHTML = `
            <span class="dropdown-title">${book.title}</span>
            <span class="dropdown-author">${book.author || "Autor desconhecido"}</span>
        `;
        item.onclick = () => selectBook(book);
        dropdown.appendChild(item);
    });

    dropdown.classList.remove("hidden");
}

function selectBook(book) {
    document.getElementById("f-title").value = book.title;
    document.getElementById("f-author").value = book.author || "";
    document.getElementById("f-year").value = book.year || "";

    if (book.cover) {
        const img = document.getElementById("img-preview");
        img.src = book.cover;
        img.classList.add("visible");
        document.querySelector("#img-label i").style.display = "none";
        document.querySelector("#img-label span").style.display = "none";
        openLibraryCover = book.cover;
    }

    const dropdown = document.getElementById("search-dropdown");
    dropdown.innerHTML = "";
    dropdown.classList.add("hidden");
}

// ————— SUBMIT —————

async function submitBook() {
    const title = document.getElementById("f-title").value.trim();
    const author = document.getElementById("f-author").value;
    const genre = document.getElementById("f-genre").value;
    const year = document.getElementById("f-year").value;
    const readDate = document.getElementById("f-read").value;
    const rating = document.getElementById("f-rating").value;
    const review = document.getElementById("f-review").value;
    const imageFile = document.getElementById("img-input").files[0];

    if (!title) return alert("Informe o título do livro!");

    const formData = new FormData();
    formData.append("title", title);
    formData.append("author", author);
    formData.append("genre", genre);
    formData.append("year", year);
    formData.append("read_date", readDate);
    formData.append("rating", rating);
    formData.append("review", review);
    if (imageFile) formData.append("image", imageFile);
    if (openLibraryCover && !imageFile) formData.append("poster_url", openLibraryCover);

    await fetch("/books", { method: "POST", body: formData });

    document.getElementById("f-title").value = "";
    document.getElementById("f-author").value = "";
    document.getElementById("f-genre").value = "";
    document.getElementById("f-year").value = "";
    document.getElementById("f-read").value = "";
    document.getElementById("f-rating").value = "0";
    document.getElementById("f-review").value = "";
    document.getElementById("img-input").value = "";
    const imgPreview = document.getElementById("img-preview");
    imgPreview.src = "";
    imgPreview.classList.remove("visible");
    document.querySelector("#img-label i").style.display = "";
    document.querySelector("#img-label span").style.display = "";
    document.querySelectorAll("#stars-input span").forEach(s => s.classList.remove("active"));
    openLibraryCover = "";
    toggleForm();

    await loadBooks();
    currentIndex = books.length;
    showSlide(currentIndex);
}

// ————— LIVROS —————

async function loadBooks() {
    const res = await fetch("/books");
    books = await res.json();
    renderBooks();
}

function renderBooks() {
    document.querySelectorAll(".book-card").forEach(c => c.remove());

    const addCard = document.getElementById("add-card");

    books.forEach((book, index) => {
        const card = document.createElement("div");
        card.className = "card book-card";
        card.innerHTML = `
            <div class="card-left">
                <img src="${book.cover_url}" alt="${book.title}">
            </div>
            <div class="card-right">
                <h2>${book.title.toUpperCase()}</h2>
                <div class="book-details">
                    <span class="year">${book.year || "—"}</span>
                    <span class="author">${book.author || "—"}</span>
                    <span class="genre">${book.genre || "—"}</span>
                </div>
                <div class="book-stars">
                    ${"★".repeat(book.rating).replace(/★/g, '<span class="active">★</span>') +
                    "★".repeat(10 - book.rating).replace(/★/g, '<span>★</span>')}
                </div>
                <p class="book-review">${book.review || ""}</p>
                <div class="book-footer">
                    <span class="read-date">Lido em ${book.read_date ? book.read_date.split('-').reverse().join('/') : "—"}</span>
                    <button class="delete-btn" onclick="deleteBook(${index})">Remover</button>
                </div>
            </div>
        `;
        addCard.insertAdjacentElement("afterend", card);
    });

    showSlide(currentIndex);
}

async function deleteBook(index) {
    await fetch(`/books/${index}`, { method: "DELETE" });
    currentIndex = 0;
    await loadBooks();
}

// ————— EXPORT / IMPORT —————

async function exportBooks() {
    window.location.href = "/books/export";
}

async function importBooks(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/books/import", { method: "POST", body: formData });
    const data = await res.json();
    console.log("Importado:", data);

    event.target.value = "";
    currentIndex = 0;
    await loadBooks();
}

document.addEventListener("click", function(e) {
    const dropdown = document.getElementById("search-dropdown");
    const searchArea = document.getElementById("f-title");
    if (!dropdown.contains(e.target) && e.target !== searchArea) {
        dropdown.classList.add("hidden");
    }
});

loadBooks();