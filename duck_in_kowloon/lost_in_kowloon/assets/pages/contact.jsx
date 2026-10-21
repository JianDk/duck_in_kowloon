import React from 'react'
import './../../static/tailwindcss/input.css'
import { createRoot } from 'react-dom/client';
import { GoogleReCaptchaProvider } from '@google-recaptcha/react';
import { Contact } from '../components/contact';

const contactContainer = document.getElementById("contact");
const siteKey = contactContainer.dataset.recaptchaSiteKey;

createRoot(contactContainer).render(
    <React.StrictMode>
        <GoogleReCaptchaProvider type="v3" siteKey={siteKey} isEnterprise>
            <Contact />
        </GoogleReCaptchaProvider>
    </React.StrictMode>
)