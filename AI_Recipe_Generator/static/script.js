// Theme Management
const themeToggleBtn = document.getElementById('themeToggle');
const themeIcon = themeToggleBtn.querySelector('i');

// Check local storage for theme
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.replace('light-theme', 'dark-theme');
    themeIcon.classList.replace('fa-moon', 'fa-sun');
}

themeToggleBtn.addEventListener('click', () => {
    if (document.body.classList.contains('light-theme')) {
        document.body.classList.replace('light-theme', 'dark-theme');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.classList.replace('dark-theme', 'light-theme');
        themeIcon.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('theme', 'light');
    }
});

// Quick Ingredient Chips Handler
function addChip(text) {
    const textarea = document.getElementById('ingredients');
    textarea.value = text;
    textarea.focus();
}

// Generate Recipe API Handler
async function generateRecipe() {
    const ingredients = document.getElementById('ingredients').value.trim();
    const dietary = document.getElementById('dietary').value;
    const cuisine = document.getElementById('cuisine').value;
    const spiceLevel = document.getElementById('spice_level').value;
    const mealType = document.getElementById('meal_type').value;

    if (!ingredients) {
        alert('Please enter at least one ingredient.');
        return;
    }

    const emptyState = document.getElementById('emptyState');
    const loadingState = document.getElementById('loadingState');
    const recipeOutput = document.getElementById('recipeOutput');
    const recipeContent = document.getElementById('recipeContent');
    const submitBtn = document.getElementById('submitBtn');

    // Show Loading UI
    emptyState.classList.add('hidden');
    recipeOutput.classList.add('hidden');
    loadingState.classList.remove('hidden');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';

    try {
        const response = await fetch('/api/generate-recipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ingredients: ingredients,
                dietary: dietary,
                cuisine: cuisine,
                spice_level: spiceLevel,
                meal_type: mealType
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Render Markdown Output
            recipeContent.innerHTML = marked.parse(data.recipe);
            loadingState.classList.add('hidden');
            recipeOutput.classList.remove('hidden');
        } else {
            alert(data.error || 'Failed to generate recipe. Please try again.');
            loadingState.classList.add('hidden');
            emptyState.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error generating recipe:', error);
        alert('An unexpected network error occurred. Please check your server connection.');
        loadingState.classList.add('hidden');
        emptyState.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Generate Recipe with AI';
    }
}

// Copy Recipe to Clipboard
function copyRecipe() {
    const content = document.getElementById('recipeContent').innerText;
    navigator.clipboard.writeText(content).then(() => {
        alert('Recipe copied to clipboard!');
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}
