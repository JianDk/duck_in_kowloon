
import { useEffect, useRef, useState } from "react";
import {
    Box,
    TextField,
    Button,
} from "@mui/material";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import { useGoogleReCaptcha } from "@google-recaptcha/react";
import {
    ContactRecaptchaError,
    executeContactRecaptcha,
    submit_contact_form_handler,
} from "../utils/recaptcha.js";

function validateContactForm(values) {
    const errors = {};
    const name = values.name.trim();
    const phone = values.phone.trim();
    const email = values.email.trim();

    if (name.length < 3) {
        errors.name = "Enter a name with at least 3 characters.";
    } else if (name.length > 100) {
        errors.name = "Use no more than 100 characters.";
    }

    if (!phone) {
        errors.phone = "Enter your phone number.";
    } else if (!/^[0-9+()\s-]{6,30}$/.test(phone)) {
        errors.phone = "Enter a phone number with 6 to 30 characters using digits, spaces, +, parentheses or hyphens.";
    }

    if (!email) {
        errors.email = "Enter your email address.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errors.email = "Enter a valid email address.";
    }

    if (!values.message.trim()) {
        errors.message = "Enter your message.";
    } else if (values.message.length > 500) {
        errors.message = "Use no more than 500 characters.";
    }

    return errors;
}

export function Contact() {
    const { executeV3, instance, isLoading, siteKey } = useGoogleReCaptcha();
    const [formValues, setFormValues] = useState({
        'name': '',
        'phone': '',
        'email': '',
        'message': '',
    });
    const [touched, setTouched] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [serverErrors, setServerErrors] = useState({});
    const [submitMessage, setSubmitMessage] = useState("");
    const [submissionSucceeded, setSubmissionSucceeded] = useState(false);
    const [recaptchaTimedOut, setRecaptchaTimedOut] = useState(false);
    const submissionInProgress = useRef(false);
    const isMounted = useRef(false);

    const clientErrors = validateContactForm(formValues);
    const errors = { ...serverErrors, ...clientErrors };
    const isValid = Object.values(errors).every((error) => !error);
    const isRecaptchaReady = Boolean(siteKey && instance && !isLoading && !recaptchaTimedOut);
    const hasRecaptchaError = !siteKey || recaptchaTimedOut || (!isLoading && !instance);
    const isSendDisabled = !isValid || isSubmitting || !isRecaptchaReady;

    useEffect(() => {
        isMounted.current = true;
        return () => {
            isMounted.current = false;
        };
    }, []);

    useEffect(() => {
        if (!isLoading) return;
        const timer = setTimeout(() => setRecaptchaTimedOut(true), 10000);
        return () => clearTimeout(timer);
    }, [isLoading]);

    let recaptchaMessage = "";
    if (hasRecaptchaError) {
        recaptchaMessage = "Security verification is unavailable. Please reload the page and try again.";
    } else if (isLoading) {
        recaptchaMessage = "Loading security verification...";
    }

    function handleChange(event) {
        const { name, value } = event.target;
        setFormValues((previous) => ({
            ...previous,
            [name]: name === "message" ? value.slice(0, 500) : value,
        }));
        setTouched((previous) => ({ ...previous, [name]: true }));
        setServerErrors((previous) => {
            const remaining = { ...previous };
            delete remaining[name];
            return remaining;
        });
        setSubmitMessage("");
        setSubmissionSucceeded(false);
    }

    function showSubmissionErrors(responseData) {
        const fieldErrors = {};

        for (const field of Object.keys(formValues)) {
            const messages = responseData?.fieldErrors?.[field];
            if (Array.isArray(messages)) {
                const textMessages = messages.filter((message) => typeof message === "string");
                fieldErrors[field] = textMessages.join(" ");
            }
        }

        setServerErrors(fieldErrors);

        const hasFieldErrors = Object.values(fieldErrors).some(Boolean);
        if (hasFieldErrors) {
            setSubmitMessage("Please correct the highlighted fields.");
        } else if (typeof responseData?.error === "string") {
            setSubmitMessage(responseData.error);
        } else {
            setSubmitMessage("Your message could not be sent. Please reload the page and try again.");
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();
        if (submissionInProgress.current || !isRecaptchaReady) return;

        setServerErrors({});
        setSubmitMessage("");
        setSubmissionSucceeded(false);
        setTouched({ name: true, phone: true, email: true, message: true });
        const validationErrors = validateContactForm(formValues);
        const hasValidationErrors = Object.keys(validationErrors).length > 0;
        if (hasValidationErrors) return;

        submissionInProgress.current = true;
        setIsSubmitting(true);

        try {
            const token = await executeContactRecaptcha(executeV3);
            if (!isMounted.current) return;

            const response = await submit_contact_form_handler({
                formValues,
                token,
            });

            let responseData = null;
            const responseIsJson = response.headers.get("content-type")?.includes("application/json");
            if (responseIsJson) {
                responseData = await response.json();
            }
            if (!isMounted.current) return;

            if (!response.ok) {
                showSubmissionErrors(responseData);
                return;
            }

            if (responseData?.success !== true) {
                throw new Error("Contact submission was not confirmed.");
            }

            setFormValues({ name: "", phone: "", email: "", message: "" });
            setTouched({});
            setSubmissionSucceeded(true);
            setSubmitMessage("Your message has been sent.");
        } catch (error) {
            if (!isMounted.current) return;
            if (error instanceof ContactRecaptchaError) {
                setSubmitMessage(error.message);
            } else {
                setSubmitMessage("Your message could not be confirmed. Please try again later.");
            }
        } finally {
            submissionInProgress.current = false;
            if (isMounted.current) setIsSubmitting(false);
        }
    }

    return (
        <section
            id="contact-section"
            aria-labelledby="contact-heading"
            className="bg-surface px-4 py-12 font-sans text-ink sm:px-6 sm:py-16 lg:px-8 lg:py-20"
        >
            <div className="mx-auto w-full max-w-3xl">

                {/* Heading */}
                <div className="mb-8 text-center sm:mb-10">
                    <p className="mb-2 font-sans text-xs font-semibold uppercase text-accent-ink">
                        Get in touch
                    </p>

                    <h1 id="contact-heading" className="font-heading text-3xl font-bold leading-tight text-primary sm:text-4xl lg:text-5xl">
                        We'd love to hear from you
                    </h1>

                    <div className="mx-auto mt-4 h-1 w-16 rounded-full bg-accent"></div>

                    <p className="mx-auto mt-4 max-w-xl font-sans text-sm leading-6 text-ink-muted sm:text-base sm:leading-7">
                        Have a question about our menu, your visit, or
                        anything else? Send us a message and we'll get
                        back to you as soon as we can.
                    </p>
                </div>

                {/* Form */}
                <Box
                    component="form"
                    noValidate
                    aria-busy={isSubmitting}
                    onSubmit={handleSubmit}
                    className="rounded-lg border border-outline bg-surface-raised p-4 shadow-sm sm:p-6 lg:p-8"
                    sx={{
                        fontFamily: "inherit",
                        "& .MuiInputBase-root": {
                            fontFamily: "inherit",
                            fontSize: "1rem",
                            color: "var(--color-ink)",
                        },
                        "& .MuiInputLabel-root": {
                            fontFamily: "inherit",
                        },
                        "& .MuiInputLabel-root:not(.Mui-error)": {
                            color: "var(--color-ink-muted)",
                        },
                        "& .MuiFormHelperText-root": {
                            fontFamily: "inherit",
                            marginLeft: 0,
                        },
                        "& .MuiFormHelperText-root:not(.Mui-error)": {
                            color: "var(--color-ink-muted)",
                        },
                        "& .MuiOutlinedInput-root": {
                            borderRadius: "8px",
                            backgroundColor: "var(--color-surface-raised)",
                            "&:not(.Mui-error) fieldset": {
                                borderColor: "var(--color-outline)",
                            },
                            "&:not(.Mui-error):hover fieldset": {
                                borderColor: "var(--color-primary)",
                            },
                            "&:not(.Mui-error).Mui-focused fieldset": {
                                borderColor: "var(--color-accent-ink)",
                                borderWidth: "1px",
                            },
                        },
                        "& .MuiInputLabel-root.Mui-focused:not(.Mui-error)": {
                            color: "var(--color-accent-ink)",
                        },
                    }}
                >
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 sm:gap-6">

                        {/* Name */}
                        <TextField
                            id="contact-name"
                            label="Name"
                            name="name"
                            placeholder="Your full name"
                            autoComplete="name"
                            fullWidth
                            required
                            variant="outlined"
                            error={Boolean(touched.name && errors.name)}
                            helperText={touched.name ? errors.name : ""}
                            value={formValues.name}
                            onChange={handleChange}
                            disabled={isSubmitting}
                        />

                        {/* Phone */}
                        <TextField
                            id="contact-phone"
                            label="Phone number"
                            name="phone"
                            placeholder="Your phone number"
                            type="tel"
                            autoComplete="tel"
                            fullWidth
                            required
                            variant="outlined"
                            error={Boolean(touched.phone && errors.phone)}
                            helperText={touched.phone ? errors.phone : ""}
                            value={formValues.phone}
                            onChange={handleChange}
                            disabled={isSubmitting}
                        />

                        {/* Email */}
                        <div className="min-w-0 sm:col-span-2">
                            <TextField
                                id="contact-email"
                                label="Email"
                                name="email"
                                placeholder="you@example.com"
                                type="email"
                                autoComplete="email"
                                fullWidth
                                required
                                variant="outlined"
                                error={Boolean(touched.email && errors.email)}
                                helperText={touched.email ? errors.email : ""}
                                value={formValues.email}
                                onChange={handleChange}
                                disabled={isSubmitting}
                            />
                        </div>

                        {/* Message */}
                        <div className="min-w-0 sm:col-span-2">
                            <TextField
                                id="contact-message"
                                label="Your message"
                                name="message"
                                placeholder="How can we help you?"
                                multiline
                                minRows={5}
                                maxRows={8}
                                error={Boolean(touched.message && errors.message)}
                                value={formValues.message}
                                onChange={handleChange}
                                disabled={isSubmitting}
                                slotProps={{
                                    htmlInput: {
                                        maxLength: 500,
                                    },
                                }}
                                helperText={
                                    <>
                                        {touched.message && errors.message && (
                                            <span className="block">{errors.message}</span>
                                        )}
                                        <span className="block">{formValues.message.length}/500 characters</span>
                                    </>
                                }
                                fullWidth
                                required
                                variant="outlined"
                            />
                        </div>
                    </div>

                    {recaptchaMessage && (
                        <p
                            id="contact-recaptcha-status"
                            role="status"
                            className={`mt-5 font-sans text-sm ${hasRecaptchaError ? "text-red-700" : "text-ink-muted"}`}
                        >
                            {recaptchaMessage}
                        </p>
                    )}

                    {submitMessage && (
                        <p
                            role="status"
                            className={`mt-5 font-sans text-sm ${submissionSucceeded ? "text-ink" : "text-red-700"}`}
                        >
                            {submitMessage}
                        </p>
                    )}

                    {/* Footer and submit */}
                    <div className="mt-6 flex flex-col gap-4 border-t border-outline pt-5 sm:mt-8 sm:flex-row sm:items-center sm:justify-between sm:pt-6">
                        <p className="min-w-0 font-sans text-sm leading-6 text-ink-muted">
                            We look forward to hearing from you.
                        </p>

                        <Button
                            type="submit"
                            variant="contained"
                            endIcon={<SendRoundedIcon />}
                            sx={{
                                width: { xs: "100%", sm: "auto" },
                                minHeight: 48,
                                flexShrink: 0,
                                px: 4,
                                py: 1.25,
                                borderRadius: "8px",
                                backgroundColor: "var(--color-primary)",
                                color: "var(--color-surface-raised)",
                                fontFamily: "inherit",
                                fontSize: "1rem",
                                fontWeight: 600,
                                textTransform: "none",
                                boxShadow: "none",
                                "&:hover": {
                                    backgroundColor: "var(--color-primary-hover)",
                                    boxShadow: "none",
                                },
                                "&:focus-visible": {
                                    outline: "2px solid var(--color-accent-ink)",
                                    outlineOffset: "4px",
                                },
                            }}
                            aria-describedby={!isRecaptchaReady ? "contact-recaptcha-status" : undefined}
                            disabled={isSendDisabled}
                            loading={isSubmitting}
                        >
                            Send message
                        </Button>
                    </div>
                </Box>
            </div>
        </section>
    );
}
