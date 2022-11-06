import * as DataManager from "./main_data_manager.js";
import * as Helpers from "./helpers.js";


const messageContainer = document.getElementById('message-container');

const deckSelectionControls = document.getElementById('deck-selection-controls');
const cardAddingControls = document.getElementById('card-adding-controls');

const wordField = document.getElementById('word-field');
const contextField = document.getElementById('context');

const translationTableBody = document.getElementById('translation-table-body');
const frequencyFilterSelect = document.getElementById('frequency-filter-select');

const definitionTableBody = document.getElementById('definition-table-body');
const googleCheckbox = document.getElementById('show-google-definitions');
const collinsCheckbox = document.getElementById('show-collins-definitions');

const getInfoButton = document.getElementById('get-info-button');
const createCardButton = document.getElementById('create-card-button');

const googleLink = document.getElementById('google-link');
const collinsLink = document.getElementById('collins-link');
const cambridgeLink = document.getElementById('cambridge-link');
const oxfordLink = document.getElementById('oxford-link');


/**Initialize values and setup events */
export function initialize(settings) {
    frequencyFilterSelect.value = settings['translation_filter'];
    frequencyFilterSelect.addEventListener('input', () => DataManager.updateTranslationFilter(frequencyFilterSelect.value));

    googleCheckbox.checked = settings['add_google_definitions'];
    googleCheckbox.addEventListener('input', () => DataManager.toggleGoogleDefinitions());

    collinsCheckbox.checked = settings['add_collins_definitions'];
    collinsCheckbox.addEventListener('input', () => DataManager.toggleCollinsDefinitions());

    wordField.addEventListener("keyup", event => {
        if (event.key !== "Enter") {
            return;
        }
        getInfoButton.click();
        event.preventDefault();
    });

    Helpers.addEventHandlerProgress(getInfoButton, 'click', () => DataManager.updateWordData(wordField.value.trim()), false);

    // When card is created, all data is cleared, so button must be disabled
    Helpers.addEventHandlerProgress(createCardButton, 'click', () => DataManager.createAnkiCard(contextField.value.trim()), true);

    const language = settings['translate_to'];
    enableOrDisableWordRelatedControls(language);
    wordField.addEventListener('input', () => enableOrDisableWordRelatedControls(language));
}

export function reset() {
    messageContainer.innerHTML = '';
    wordField.value = '';
    contextField.value = '';
    translationTableBody.innerHTML = '';
    definitionTableBody.innerHTML = '';
    disableWordRelatedControls();
}

export function clearMessages() {
    messageContainer.innerHTML = '';
}

export function showInfo(message, timeout = null) {
    showMessage('info', message, timeout);
}

export function showError(message, timeout = null) {
    showMessage('danger', message, timeout);
}

/** Fill deck selector with options and show it */
export function showDeckSelectorControls(deckNamesAndIds) {
    const deckSelector = deckSelectionControls.getElementsByTagName('select')[0];

    for (const [dName, dId] of Object.entries(deckNamesAndIds)) {
        const opt = document.createElement('option');
        opt.value = dId;
        opt.innerHTML = dName;
        deckSelector.appendChild(opt);
    }

    document.getElementById('submit-deck-id').addEventListener('click', async () => {
        const deckName = deckSelector.options[deckSelector.selectedIndex].text;
        await DataManager.updateDeck(deckName, deckSelector.value);
        showCardAddingControls();
    });

    deckSelectionControls.classList.remove('hidden');
}

export function showCardAddingControls() {
    deckSelectionControls.remove();
    cardAddingControls.classList.remove('hidden');
}

export function update(wordData, settings) {
    updateTranslations(wordData, settings);
    updateDefinitions(wordData, settings);
}


export function blockCardCreation() {
    createCardButton.disabled = true;
}


function enableOrDisableWordRelatedControls(language) {
    const word = wordField.value.trim();
    if (word.length == 0) {
        disableWordRelatedControls();
    }
    else {
        enableWordRelatedControls(word, language);
    }
}

function disableWordRelatedControls() {
    getInfoButton.disabled = true;
    googleLink.removeAttribute('href');
    collinsLink.removeAttribute('href');
    cambridgeLink.removeAttribute('href');
    oxfordLink.removeAttribute('href');
}

function enableWordRelatedControls(word, language) {
    getInfoButton.disabled = false;
    googleLink.setAttribute('href', `https://translate.google.com/?sl=en&tl=${language}&text=${word}`);
    collinsLink.setAttribute('href', `https://www.collinsdictionary.com/dictionary/english/${word}`);
    cambridgeLink.setAttribute('href', `https://dictionary.cambridge.org/dictionary/english/${word}`);
    oxfordLink.setAttribute('href', `https://www.oxfordlearnersdictionaries.com/definition/english/${word}`);
}

function updateTranslations(wordData, settings) {
    translationTableBody.innerHTML = '';
    const filtered = wordData['translations'].filter(tr => tr['frequency'] >= settings['translation_filter']);

    createCardButton.disabled = filtered.length == 0;

    let number = 1;
    filtered.forEach(translation => {
        const row = createTranslationRow(translation, number);
        translationTableBody.appendChild(row);
        number += 1;
    });
}

function updateDefinitions(wordData, settings) {
    definitionTableBody.innerHTML = '';

    let number = 1;
    if (settings['add_google_definitions']) {
        const googleData = wordData['google'];
        googleData['definitions'].forEach(def => {
            const row = createGoogleDefinitionRow(def, number);
            definitionTableBody.appendChild(row);
            number += 1;
        });
    }

    if (settings['add_collins_definitions']) {
        const collinsData = wordData['collins'];
        collinsData['definitions'].forEach(def => {
            const row = createCollinsDefinitionRow(def, number);
            definitionTableBody.appendChild(row);
            number += 1;
        });
    }
}

function showMessage(level, message, timeout) {
    const div = document.createElement('div');
    div.classList.add('alert', `alert-${level}`, 'alert-dismissible', 'fade', 'show');
    div.setAttribute('role', 'alert');
    div.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
    if (timeout) {
        setTimeout(() => div.remove(), timeout * 1000);
    }
    messageContainer.prepend(div);
}

function createTranslationRow(translation, number) {
    const row = Helpers.createTranslationRow(translation, number);
    addDeleteButton(row, () => DataManager.deleteTranslation(translation['translation']));
    return row;
}

function createGoogleDefinitionRow(def, number) {
    const row = Helpers.createGoogleDefinitionRow(def, number, true);
    addDeleteButton(row, () => DataManager.deleteGoogleDefinition(def['definition']));
    return row;
}

function createCollinsDefinitionRow(def, number) {
    const row = Helpers.createCollinsDefinitionRow(def, number, true);
    addDeleteButton(row, () => DataManager.deleteCollinsDefinition(def['definition']));
    return row;
}

/**Adds a button that deletes the row and it's data from 'wordData'
* @param {*} row row to add delete button to
* @param {*} deleteAction additional action that deletes data
*/
function addDeleteButton(row, deleteAction) {
    const button = document.createElement('button');
    button.setAttribute('title', 'Delete');
    button.classList.add('btn', 'btn-close');
    button.addEventListener('click', () => {
        row.remove();
        deleteAction();
    });

    const td = document.createElement('td');
    td.appendChild(button);

    row.appendChild(td);
}