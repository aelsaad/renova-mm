/* RENOVA MM — site settings.
   Edit the phone number and email here; they update everywhere on the site. */
window.RENOVA = {
  /* Public address of the site, with a trailing slash. Change it when renovamm.fr is connected. */
  siteUrl: "https://aelsaad.github.io/renova-mm/",
  /* false = hidden from Google (noindex). Set to true at the official launch, then run tools/build.py. */
  listed: false,
  /* Visitor statistics: paste the token from Cloudflare → Web Analytics (snippet "token": "…"),
     then run tools/build.py. Empty = no statistics. Cookie-free, so no cookie banner is needed. */
  cloudflareAnalyticsToken: "",

  phone: "+33695010383",
  email: "info@renovamm.fr",

  /* Social networks — paste the link to each page.
     Leave a link empty ("") to hide that icon. WhatsApp uses the phone number above. */
  social: {
    facebook: "#",
    instagram: "",
    tiktok: "#",
    linkedin: "",
    whatsapp: true
  },

  /* "Nos réalisations" 3D carousel — files live in assets/photos/ */
  gallery: [
    { src: "assets/photos/cuisine-anthracite.webp", fr: "Cuisine équipée", en: "Fitted kitchen" },
    { src: "assets/photos/salle-de-bains.webp", fr: "Salle de bains", en: "Bathroom" },
    { src: "assets/photos/verriere-parquet.webp", fr: "Verrière & parquet", en: "Glass partition & flooring" },
    { src: "assets/photos/pose-stratifie.webp", fr: "Pose de stratifié", en: "Laminate flooring" },
    { src: "assets/photos/cuisine-verte.webp", fr: "Cuisine sur mesure", en: "Custom kitchen" },
    { src: "assets/photos/terrasse-bois.webp", fr: "Terrasse bois", en: "Wooden deck" },
    { src: "assets/photos/combles.webp", fr: "Combles aménagés", en: "Converted attic" }
  ]
};
