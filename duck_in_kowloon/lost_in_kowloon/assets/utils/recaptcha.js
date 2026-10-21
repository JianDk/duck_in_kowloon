export class ContactRecaptchaError extends Error {}

export async function executeContactRecaptcha(executeV3) {
    if (typeof executeV3 !== "function") {
        throw new ContactRecaptchaError("Security verification is unavailable. Please reload the page and try again.");
    }

    let timeout;
    try {
        const deadline = new Promise((_, reject) => {
            timeout = setTimeout(() => reject(new ContactRecaptchaError()), 10000);
        });
        const token = await Promise.race([
            executeV3("contact_submit"),
            deadline,
        ]);
        if (typeof token !== "string" || !token.trim()) {
            throw new ContactRecaptchaError();
        }
        return token;
    } catch {
        throw new ContactRecaptchaError("Security verification could not be completed. Please try again.");
    } finally {
        clearTimeout(timeout);
    }
}

export async function submit_contact_form_handler({
    formValues,
    token,
}) {
    const contactElement = document.getElementById("contact");
    const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
    const submitUrl = contactElement?.dataset.submitUrl;
    const csrfToken = csrfInput?.value;

    if (!submitUrl || !csrfToken) {
        throw new Error("Contact submission configuration is unavailable.");
    }

    const response = await fetch(submitUrl, {
        method: "POST",
        mode: "same-origin",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ ...formValues, recaptchaToken: token }),
    });

    return response;
}