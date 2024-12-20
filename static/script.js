// Query selectors for the toggle functionality
const container = document.querySelector('.container');
const registerbtn = document.querySelector('.register-btn');
const loginbtn = document.querySelector('.login-btn');

// Toggle between register and login views
registerbtn.addEventListener('click', () => {
    container.classList.add('active');
});

loginbtn.addEventListener('click', () => {
    container.classList.remove('active');
});

// Query selectors for form elements
const loginForm = document.querySelector('.login form');
const registerForm = document.querySelector('.register form');
const firstname_input = document.querySelector('.register [placeholder="Username"]');
const email_input = document.querySelector('.register [placeholder="Email"]');
const password_input = document.querySelector('.register [placeholder="Password"]');
const login_email_input = document.querySelector('.login [placeholder="Username"]');
const login_password_input = document.querySelector('.login [placeholder="Password"]');
const repeat_password_input = null; // Placeholder, registration form doesn't have this in provided HTML
const error_message = document.getElementById('error-message') || document.createElement('div');
document.body.appendChild(error_message); // Ensure error message container is added

// Event listener for the register form
registerForm.addEventListener('submit', (e) => {
    const errors = getSignupFormErrors(
        firstname_input.value,
        email_input.value,
        password_input.value,
        password_input.value // As repeat_password_input is missing, using password_input for validation
    );

    if (errors.length > 0) {
        e.preventDefault();
        error_message.innerText = errors.join(". ");
    }
});

// Event listener for the login form
loginForm.addEventListener('submit', (e) => {
    const errors = getLoginFormErrors(login_email_input.value, login_password_input.value);

    if (errors.length > 0) {
        e.preventDefault();
        error_message.innerText = errors.join(". ");
    }
});

// Function to validate the signup form
function getSignupFormErrors(firstname, email, password, repeatPassword) {
    const errors = [];

    if (firstname === '' || firstname == null) {
        errors.push('Firstname is required');
        firstname_input.parentElement.classList.add('incorrect');
    }
    if (email === '' || email == null) {
        errors.push('Email is required');
        email_input.parentElement.classList.add('incorrect');
    }
    if (password === '' || password == null) {
        errors.push('Password is required');
        password_input.parentElement.classList.add('incorrect');
    }
    if (password.length < 8) {
        errors.push('Password must have at least 8 characters');
        password_input.parentElement.classList.add('incorrect');
    }
    if (password !== repeatPassword) {
        errors.push('Password does not match repeated password');
        password_input.parentElement.classList.add('incorrect');
    }

    return errors;
}

// Function to validate the login form
function getLoginFormErrors(email, password) {
    const errors = [];

    if (email === '' || email == null) {
        errors.push('Email is required');
        login_email_input.parentElement.classList.add('incorrect');
    }
    if (password === '' || password == null) {
        errors.push('Password is required');
        login_password_input.parentElement.classList.add('incorrect');
    }

    return errors;
}

// Clear error messages and input highlight on input change
const allInputs = [
    firstname_input,
    email_input,
    password_input,
    login_email_input,
    login_password_input
].filter(input => input != null);

allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if (input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect');
            error_message.innerText = '';
        }
    });
});
