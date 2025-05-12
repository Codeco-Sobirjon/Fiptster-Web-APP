document.addEventListener('DOMContentLoaded', function () {
    function toggleSecretCode() {
        const taskTypeSelect = document.getElementById('id_task_type');
        const secretCodeInput = document.getElementById('id_secret_code');

        if (taskTypeSelect && secretCodeInput) {
            if (taskTypeSelect.value === 'FIPT Youtube') {
                secretCodeInput.removeAttribute('disabled');
                secretCodeInput.removeAttribute('title');
                secretCodeInput.style.cursor = 'text';
            } else {
                secretCodeInput.setAttribute('disabled', 'disabled');
                secretCodeInput.setAttribute('title', 'Доступно только для задачи FIPT Youtube');
                secretCodeInput.style.cursor = 'not-allowed';
            }
        }
    }

    const taskTypeSelect = document.getElementById('id_task_type');
    const secretCodeInput = document.getElementById('id_secret_code');

    if (taskTypeSelect && secretCodeInput) {
        taskTypeSelect.addEventListener('change', toggleSecretCode);
        toggleSecretCode();

        secretCodeInput.addEventListener('mouseenter', function () {
            if (secretCodeInput.disabled) {
                secretCodeInput.setAttribute('title', 'Доступно только для задачи FIPT Youtube');
            }
        });

        secretCodeInput.addEventListener('click', function (e) {
            if (secretCodeInput.disabled) {
                e.preventDefault();
                alert('Поле доступно только при выборе "FIPT Youtube"');
            }
        });
    }
});
