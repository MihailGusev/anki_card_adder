import * as InterfaceManager from './main_interface_manager.js';

/** Needed to post data back to the server */
const csrftoken = getCookie('csrftoken');

/** Needed to filter and transform frequency from number to word */
const frequencyMapping = { 1: 'Rare', 2: 'Uncommon', 3: 'Common' };

/** Creates HTML markup for a single translation (for browser and Anki card) */
export function createTranslationRow(translation, number) {
    const row = document.createElement('tr');
    const frequency = frequencyMapping[translation['frequency']];
    row.innerHTML = `
        <th scope="row">${number}</th>
        <td>${translation['part_of_speech']}</td>
        <td>${translation['translation']}</td>
        <td>${translation['reverse_translations'].join(', ')}</td>
        <td>${frequency}</td>`;
    return row;
}

/** Creates HTML markup for a single definition from Google (for browser and Anki card). 
 * The main purpose of 'Tags' and 'Source' columns is filtering,
 * so we only need them in browser and not inside Anki card */
export function createGoogleDefinitionRow(def, number, browser) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <th scope="row">${number}</th>
        <td>${def['part_of_speech']}</td>
        <td>${def['definition']}</td>
        <td>${def['example']}</td>
        <td>${def['synonyms'].join(', ')}</td>`;
    if (browser) {
        row.innerHTML += `
        <td>${def['tags'].join(', ')}</td>
        <td>Google</td>`;
    }
    return row;
}

/** Creates HTML markup for a single definition from Collins (for browser and Anki card). 
 * The main purpose of 'Tags' and 'Source' columns is filtering,
 * so we only need them in browser and not inside Anki card.
 * Collins's American-Learner dictionary does not provide synonyms, 
 * but all definitions are in one table, so we need empty <td> tag */
export function createCollinsDefinitionRow(def, number, browser) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <th scope="row">${number}</th>
        <td>${def['part_of_speech']}</td>
        <td>${def['definition']}</td>
        <td>${def['examples'].join('\n\n')}</td>
        <td></td>`;

    if (browser) {
        row.innerHTML += `
            <td>${def['tags'].join(', ')}</td>
            <td>Collins</td>`;
    }
    return row;
}

/** Fetches and returns JSON data from a given URL */
export async function getJson(url) {
    try {
        const result = await fetch(url);
        if (!result.ok) {
            throw new Error(`${result.statusText} (${result.status})`);
        }
        return await result.json();
    }
    catch (err) {
        throw err;
    }
}

/** Transforms data into JSON and posts it to a given URL */
export async function postJson(url, data) {
    const result = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(data),
    });

    if (!result.ok) {
        throw new Error(`${result.statusText} (${result.status})`);
    }
}

/**
   Updates learner settings by posting key-value pairs 
   that corresponds to the 'Settings' django model:
   language: string (language code)

   deck_id: int
   note_id: int

   translation_filter: int

   add_collins_definitions: bool
   add_google_definitions: bool

   show_message_on_card_addition: bool

   @param settingsPage Settings can be updated from main or settings page.
   We only need to show messages on the settings page
 */
export async function updateLearnerSettings(settings, settingsPage) {
    try {
        await postJson('/account/settings/', settings);
        if (settingsPage) {
            InterfaceManager.showInfo('Settings have been updated', 2);
        }
    }
    catch (err) {
        if (settingsPage) {
            InterfaceManager.showError('Unable to update settings');
        }
        throw err;
    }
}

/** Adds event listener to @param input, making @param disabled when @param input is blank */
export function enableControlWhenTextIsNotBlank(control, input) {
    control.disabled = input.value.trim().length == 0;
    input.addEventListener('input', ev => {
        control.disabled = ev.target.value.trim().length == 0;
    });
}

/**Adds event listener to a control. 
 * While event is being handled, control gets disabled and displays progress spinner
 * @param disable if true, control will be disabled after successfull promise await
 */
export async function addEventHandlerProgress(control, event, promise, disable) {
    control.addEventListener(event, async () => {
        const html = control.innerHTML;
        control.disabled = true;
        control.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                             ${html}`;
        try {
            await promise();
            control.disabled = disable;
        }
        catch {
            control.disabled = false;
        }
        finally {
            control.innerHTML = html;
        }
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
