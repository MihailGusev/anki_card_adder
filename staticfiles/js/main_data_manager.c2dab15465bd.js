import * as AnkiActions from "./main_anki_actions.js";
import * as InterfaceManager from "./main_interface_manager.js";
import * as Helpers from "./helpers.js";

let noteName;
let deckName;
let settings; // Learner's settings
let wordData; // Translations, definitions, etc

/** Set user settings, create new note if necessary and show deck/main controls */
export async function initialize() {
    settings = JSON.parse(document.getElementById('learner-settings').textContent);
    await AnkiActions.requestAnkiPermission();

    setupNote(settings['note_id']);

    InterfaceManager.initialize(settings);

    const deckNamesAndIds = await AnkiActions.getDeckNamesAndIds();
    for (const [dName, dId] of Object.entries(deckNamesAndIds)) {
        if (dId === settings['deck_id']) {
            deckName = dName;
            InterfaceManager.showCardAddingControls();
            break;
        }
    }
    if (deckName == null) {
        InterfaceManager.showDeckSelectorControls(deckNamesAndIds);
    }
}

export async function updateDeck(dName, dId) {
    deckName = dName;
    await updateLearnerSetting('deck_id', dId, false);
}

export async function updateTranslationFilter(filterValue) {
    await updateLearnerSetting('translation_filter', filterValue, true);
}

export function deleteTranslation(translation) {
    wordData['translations'] = wordData['translations'].filter(tr => tr['translation'] !== translation);
    const filtered = wordData['translations'].filter(tr => tr['frequency'] >= settings['translation_filter']);
    if (filtered.length == 0) {
        InterfaceManager.blockCardCreation();
    }
}

export function deleteGoogleDefinition(definition) {
    wordData['google']['definitions'] = wordData['google']['definitions'].filter(def => def['definition'] !== definition);
}

export function deleteCollinsDefinition(definition) {
    wordData['collins']['definitions'] = wordData['collins']['definitions'].filter(def => def['definition'] !== definition);
}

export async function toggleGoogleDefinitions() {
    await updateLearnerSetting('add_google_definitions', !settings['add_google_definitions'], true);
}

export async function toggleCollinsDefinitions() {
    await updateLearnerSetting('add_collins_definitions', !settings['add_collins_definitions'], true);
}

/**Replaces old data with new one and updates interface
 * @param {string} word 
 */
export async function updateWordData(word) {
    InterfaceManager.clearMessages();
    try {
        wordData = await Helpers.getJson(`word-data/${word}`);
    }
    catch (err) {
        InterfaceManager.showError('Unable to get word data from the server');
        throw err;
    }

    if (wordData['errors']) {
        InterfaceManager.reset();
        wordData['errors'].forEach(err => InterfaceManager.showError(err));
        wordData = null;
    }
    else {
        InterfaceManager.update(wordData, settings);
    }
}

/**Creates new card for the word
 * @param {string} context 
 */
export async function createAnkiCard(context) {
    await AnkiActions.createCard(deckName, noteName, wordData, settings, context);
    InterfaceManager.reset();
    wordData = null;
    if (settings['show_message_on_card_addition']) {
        InterfaceManager.showInfo('Created successfully', 2);
    }
}


async function setupNote(currentNoteId) {
    const noteNamesAndIds = await AnkiActions.getNoteNamesAndIds();
    // First, try to find existing note by exact id match with the current id
    noteName = await AnkiActions.getExistingNoteNameById(currentNoteId, noteNamesAndIds);
    if (noteName) {
        return;
    }

    // Then try to find a note that has all required fields for AWA to work
    const nameAndId = await AnkiActions.getExistingNoteByFields(noteNamesAndIds);
    if (nameAndId) {
        noteName = nameAndId[0];
        await updateLearnerSetting('note_id', nameAndId[1], false);
        return;
    }

    // If not found, create a new note
    const newNote = await AnkiActions.createNote();
    noteName = newNote['name'];
    await updateLearnerSetting('note_id', newNote['id'], false);
    InterfaceManager.showInfo(`A note called ${noteName} has been added to your Anki application! <hr>
                                   You can change the name of the note and the styling, but <b>don't</b> change field names!`);
}

/**Update given key with given value and send changes to backend
 * @param {string} key 
 * @param {string} value 
 * @param {boolean} updateInterface 
 */
async function updateLearnerSetting(key, value, updateInterface) {
    settings[key] = value;
    try {
        // It doesn't matter if backend updating failed
        await Helpers.updateLearnerSettings(settings, false);
    }
    finally {
        if (updateInterface) {
            InterfaceManager.update(wordData, settings);
        }
    }
}