
import { useState } from "react";
import {
    Box,
    TextField,
    Button,
} from "@mui/material";
import SendRoundedIcon from "@mui/icons-material/SendRounded";

export function Contact() {
    const [message, setMessage] = useState("");

    return (
        <section
            id="contact"
            className="bg-stone-50 px-4 py-12 font-sans sm:px-6 sm:py-16 lg:px-8 lg:py-20"
        >
            <div className="mx-auto w-full max-w-3xl">

                {/* Heading */}
                <div className="mb-8 text-center sm:mb-10">
                    <p className="mb-3 font-sans text-xs font-semibold uppercase tracking-[0.2em] text-emerald-900 sm:text-sm">
                        <span className="text-[#d6c27f]">— </span>
                        Get in touch
                        <span className="text-[#d6c27f]"> —</span>
                    </p>

                    <h2 className="font-heading text-3xl font-bold leading-tight text-emerald-950 sm:text-4xl lg:text-5xl">
                        We'd love to hear from you
                    </h2>

                    <p className="mx-auto mt-4 max-w-xl font-sans text-sm leading-6 text-stone-600 sm:text-base sm:leading-7">
                        Have a question about our menu, your visit, or
                        anything else? Send us a message and we'll get
                        back to you as soon as we can.
                    </p>
                </div>

                {/* Form */}
                <Box
                    component="form"
                    onSubmit={(event) => event.preventDefault()}
                    className="rounded-xl border border-stone-200 bg-white p-4 shadow-sm sm:rounded-2xl sm:p-7 md:p-9"
                    sx={{
                        fontFamily: "inherit",
                        "& .MuiInputBase-root": {
                            fontFamily: "inherit",
                            fontSize: "0.95rem",
                        },
                        "& .MuiInputLabel-root": {
                            fontFamily: "inherit",
                        },
                        "& .MuiFormHelperText-root": {
                            fontFamily: "inherit",
                            marginLeft: 0,
                        },
                        "& .MuiOutlinedInput-root": {
                            borderRadius: "8px",
                            backgroundColor: "#fff",
                            "& fieldset": {
                                borderColor: "#d6d3d1",
                            },
                            "&:hover fieldset": {
                                borderColor: "#065f46",
                            },
                            "&.Mui-focused fieldset": {
                                borderColor: "#065f46",
                                borderWidth: "1.5px",
                            },
                        },
                        "& .MuiInputLabel-root.Mui-focused": {
                            color: "#065f46",
                        },
                    }}
                >
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 sm:gap-6">

                        {/* Name */}
                        <TextField
                            label="Name"
                            name="name"
                            placeholder="Your full name"
                            autoComplete="name"
                            fullWidth
                            required
                            variant="outlined"
                        />

                        {/* Phone */}
                        <TextField
                            label="Phone number"
                            name="phone"
                            placeholder="Your phone number"
                            type="tel"
                            autoComplete="tel"
                            fullWidth
                            required
                            variant="outlined"
                        />

                        {/* Email */}
                        <div className="min-w-0 sm:col-span-2">
                            <TextField
                                label="Email"
                                name="email"
                                placeholder="you@example.com"
                                type="email"
                                autoComplete="email"
                                fullWidth
                                required
                                variant="outlined"
                            />
                        </div>

                        {/* Message */}
                        <div className="min-w-0 sm:col-span-2">
                            <TextField
                                label="Your message"
                                name="message"
                                placeholder="How can we help you?"
                                multiline
                                minRows={5}
                                maxRows={8}
                                value={message}
                                onChange={(event) =>
                                    setMessage(
                                        event.target.value.slice(0, 500)
                                    )
                                }
                                slotProps={{
                                    htmlInput: {
                                        maxLength: 500,
                                    },
                                }}
                                helperText={`${message.length}/500 characters`}
                                fullWidth
                                required
                                variant="outlined"
                            />
                        </div>
                    </div>

                    {/* Footer and submit */}
                    <div className="mt-6 flex flex-col gap-4 border-t border-stone-100 pt-5 sm:mt-8 sm:flex-row sm:items-center sm:justify-between sm:pt-6">
                        <p className="font-sans text-sm leading-6 text-stone-500">
                            We look forward to hearing from you.
                        </p>

                        <Button
                            type="submit"
                            variant="contained"
                            endIcon={<SendRoundedIcon />}
                            sx={{
                                width: { xs: "100%", sm: "auto" },
                                minHeight: 48,
                                px: 4,
                                py: 1.25,
                                borderRadius: "8px",
                                backgroundColor: "#065f46",
                                color: "#ffffff",
                                fontFamily: "inherit",
                                fontSize: "0.95rem",
                                fontWeight: 600,
                                textTransform: "none",
                                boxShadow: "none",
                                "&:hover": {
                                    backgroundColor: "#064e3b",
                                    boxShadow: "none",
                                },
                                "&:focus-visible": {
                                    outline: "3px solid #d6c27f",
                                    outlineOffset: "3px",
                                },
                            }}
                        >
                            Send message
                        </Button>
                    </div>
                </Box>
            </div>
        </section>
    );
}
