/**
 * Functions that work with AnkiConnect add-on
 * Reference: https://foosoft.net/projects/anki-connect/
 * Key Anki concepts: https://docs.ankiweb.net/getting-started.html#key-concepts
 */
import * as AnkiStyling from './main_anki_styling.js';
import * as InterfaceManager from './main_interface_manager.js';
import * as Helpers from './helpers.js';

const ankiConnectVersion = 6;
// Don't forget to change AnkiAppearance if changing these fields
const noteFields = ['Word', 'Transcription', 'Sound', 'Context', 'TranslateTo', 'TranslationString', 'TranslationTable', 'DefinitionTable'];
const ankiConnectAddr = 'http://127.0.0.1:8765';

/** By default, AnkiConnect only allows actions coming from localhost.
 * This function requests permission to perform actions from other urls
 * (Anki will show window with 'yes' and 'no' buttons for user to click)
 */
export async function requestAnkiPermission() {
    return await invoke('requestPermission');
}

/** @returns {Promise<Object<number, string>>} dictionary with note names as keys and ids as values */
export async function getNoteNamesAndIds() {
    // Anki's term 'Note type' corresponds to AnkiConnect's 'Model'
    return await invoke('modelNamesAndIds');
}

/** Returns note name if there is a note with a given noteId and this note has all required fields
 * otherwise returns null
 * @param {number} noteId 
 * @param {Object<string, number>} noteNamesAndIds dictionary with note names as keys and ids as values
 * @returns {Promise<string|null>} name of the existing note which id is equal to noteId or null
 */
export async function getExistingNoteNameById(noteId, noteNamesAndIds) {
    if (!noteId) {
        return null;
    }
    // First, try to find note name that corresponds to user's note id
    const nameIdPair = Object.entries(noteNamesAndIds).find(nameAndId => nameAndId[1] === noteId);

    if (!nameIdPair) {
        return null;
    }
    const noteName = nameIdPair[0];

    return hasAllRequiredFields(noteName) ? noteName : null;
}

export async function getExistingNoteByFields(noteNamesAndIds) {
    for (const nameAndId of Object.entries(noteNamesAndIds)) {
        if (await hasAllRequiredFields(nameAndId[0])) {
            return nameAndId;
        }
    }
    return null;
}

/** Creates new note and returns information about it (including id and name) */
export async function createNote() {
    const params = {
        'modelName': `AWA ${Date.now()}`, // To avoid duplicate error. User can rename it later
        'inOrderFields': noteFields,
        'css': AnkiStyling.css,
        'cardTemplates': [
            {
                // There're 2 types of cards when learning a language: Production and Recognition
                // Production is Native language is on the front of the flash card 
                // and Studied language is on the back. Recognition is opposite
                'Name': 'Production',
                'Front': AnkiStyling.frontSide,
                'Back': AnkiStyling.backSide,
            }
        ]
    };
    return await invoke('createModel', params);
}

/** @returns {Promise<Object<string, number>>} dictionary with deck names as keys and ids as values */
export async function getDeckNamesAndIds() {
    return await invoke('deckNamesAndIds');
}

export async function createCard(deckName, noteName, wordData, settings, context) {
    const params = {
        'note': {
            'deckName': deckName,
            'modelName': noteName,
            'fields': {
                'Word': wordData['word'],
                'Transcription': wordData['collins']['transcription'],
                'Context': context,
                'TranslateTo': settings['translate_to'],
                'TranslationString': getTranslationString(wordData, settings),
                'TranslationTable': getTranslationTable(wordData, settings),
                'DefinitionTable': getDefinitionTable(wordData, settings),
            },
            'options': {
                'allowDuplicate': false,
            },
            'audio': [{
                'url': wordData['collins']['audio_url'],
                'filename': `${wordData['word']}.mp3`,
                'fields': [
                    'Sound',
                ]
            }],
        }
    };
    await invoke('addNote', params);
}

/** @returns true if note has all the fields that are used by AWA */
async function hasAllRequiredFields(noteName) {
    const fields = new Set(await getNoteFields(noteName));
    if (fields.size < noteFields.length) {
        return false;
    }

    for (const field of noteFields) {
        if (!fields.has(field)) {
            return false;
        }
    }
    return true;
}

/**Get all field names that a given note has
 * @param {string} noteName 
 * @returns {Promise<Array<string>>} an array of field names
 */
async function getNoteFields(noteName) {
    const params = {
        'modelName': noteName,
    };
    return await invoke('modelFieldNames', params);
}

/**@returns filtered translations joined by comma*/
function getTranslationString(wordData, settings) {
    return wordData['translations']
        .filter(t => t['frequency'] >= settings['translation_filter'])
        .map(t => t['translation'])
        .join(', ');
}

/**@returns html markup for translation table */
function getTranslationTable(wordData, settings) {
    const table = getTableBase('Part of speech', 'Translation', 'Reverse translations', 'Frequency');
    const tbody = document.createElement('tbody');
    table.appendChild(tbody);

    wordData['translations']
        .filter(t => t['frequency'] >= settings['translation_filter'])
        .forEach((t, index) => tbody.appendChild(Helpers.createTranslationRow(t, index + 1)));
    return table.outerHTML;
}

/**@returns html markup for definition table */
function getDefinitionTable(wordData, settings) {
    const table = getTableBase('Part of speech', 'Definition', 'Examples', 'Synonyms');
    const tbody = document.createElement('tbody');
    table.appendChild(tbody);

    let number = 1;
    if (settings['add_google_definitions']) {
        const googleData = wordData['google'];
        googleData['definitions'].forEach(def => {
            const row = Helpers.createGoogleDefinitionRow(def, number, false);
            tbody.appendChild(row);
            number += 1;
        });
    }

    if (settings['add_collins_definitions']) {
        const collinsData = wordData['collins'];
        collinsData['definitions'].forEach(def => {
            const row = Helpers.createCollinsDefinitionRow(def, number, false);
            tbody.appendChild(row);
            number += 1;
        });
    }

    // If no definition were added, just return empty string instead of empty table
    if (number == 1) {
        return '';
    }
    return table.outerHTML;
}

/**@Returns html markup for table with given columns */
function getTableBase(...columnList) {
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    headRow.innerHTML += '<th>#</th>';
    columnList.forEach(col => headRow.innerHTML += `<th>${col}</th>`);
    thead.appendChild(headRow);
    table.appendChild(thead);
    return table;
}

/**
 * Core function communicating with AnkiConnect add-on
 * @param {string} action action to perform
 * @param {Object<string, any>} params parameters for the action
 * @returns {Promise<any>} the response from AnkiConnect
 */
async function invoke(action, params = {}) {
    return await fetch(ankiConnectAddr, {
        method: 'POST',
        body: JSON.stringify({ action, version: ankiConnectVersion, params })
    })
        .then(response => response.json())
        .catch(err => {
            // If something went wrong, then AnkiConnect server is likely to be offline
            InterfaceManager.showError(`Unable to connect to Anki. Make sure that Anki is opened,
            AnkiConnect add-on is installed and reload the page. Read the <a href='/guide'>Guide</a> if you haven't yet.`);
            throw err;
        })
        .then(result => {
            if (result.error !== null) {
                const message = result.error.charAt(0).toUpperCase() + result.error.substr(1);
                InterfaceManager.showError(message);
                throw new Error(result.error);
            }
            else {
                return result.result;
            }
        });
}