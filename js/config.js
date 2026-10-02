/* RENOVA MM — site settings.
   Edit the phone number and email here; they update everywhere on the site. */
window.RENOVA = {
  /* Public address of the site, with a trailing slash. Change it when renovamm.fr is connected. */
  siteUrl: "https://aelsaad.github.io/renova-mm/",
  /* false = hidden from Google (noindex). Set to true at the official launch, then run tools/build.py. */
  listed: false,
  /* Visitor statistics: paste the token from Cloudflare → Web Analytics (snippet "token": "…"),
     then run tools/build.py. Empty = no statistics. Cookie-free, so no cookie banner is needed. */
  /* Contact form: Web3Forms access key — messages go to the email address the key was created with.
     Empty = the form opens the visitor's email app instead. */
  web3formsKey: "10ccfa85-edf2-469c-b616-8c26be1361f8",
  cloudflareAnalyticsToken: "c92455e8f83347b7a79412355ab6c3ba",

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

  /* Customer reviews — REAL reviews only, with the customer's consent. The section stays hidden while the list is empty.
     One entry per review, e.g.:
     { name: "Sophie M.", city: "Bagnolet", rating: 5, lang: "fr",   (lang = language the customer wrote in)
       emoji: "😊",   (optional sticker on the name circle — 😊 by default; never put emojis inside the customer's text)
       service: { fr: "Montage de meubles", en: "Furniture assembly" },
       text: { fr: "Texte de l'avis…", en: "Review text…" } },
     Then run tools/build.py. */
  /* placeholder: true = layout preview only. These cards are dropped automatically when listed is true. */
  reviews: [
    { name: "aes", city: "Berlin", rating: 5, lang: "fr", emoji: "😊",
      text: { fr: "Travail soigné et professionnel, réalisé en un temps record. Équipe sympathique, efficace et toujours de bonne humeur ! Merci beaucoup pour votre excellent travail.",
              en: "Careful, professional work, completed in record time. A friendly, efficient team that's always in a good mood! Thank you so much for your excellent work." } },
    { name: "Test", city: "Test", rating: 5, placeholder: true,
      service: { fr: "Test", en: "Test" }, text: { fr: "test test test", en: "test test test" } },
    { name: "Test", city: "Test", rating: 5, placeholder: true,
      service: { fr: "Test", en: "Test" }, text: { fr: "test test test", en: "test test test" } },
    { name: "Test", city: "Test", rating: 5, placeholder: true,
      service: { fr: "Test", en: "Test" }, text: { fr: "test test test", en: "test test test" } },
    { name: "Test", city: "Test", rating: 5, placeholder: true,
      service: { fr: "Test", en: "Test" }, text: { fr: "test test test", en: "test test test" } },
    { name: "Test", city: "Test", rating: 5, placeholder: true,
      service: { fr: "Test", en: "Test" }, text: { fr: "test test test", en: "test test test" } }
  ],

  /* "Nos réalisations" 3D carousel — files live in assets/photos/ */
  gallery: [
    { src: "assets/photos/cuisine-anthracite.webp", fr: "Cuisine équipée", en: "Fitted kitchen" },
    { src: "assets/photos/salle-de-bains.webp", fr: "Salle de bains", en: "Bathroom" },
    { src: "assets/photos/cuisine-verriere.webp", fr: "Cuisine & verrière", en: "Kitchen & glass partition" },
    { src: "assets/photos/verriere-parquet.webp", fr: "Verrière & parquet", en: "Glass partition & flooring" },
    { src: "assets/photos/pose-stratifie.webp", fr: "Pose de stratifié", en: "Laminate flooring" },
    { src: "assets/photos/cuisine-verte.webp", fr: "Cuisine sur mesure", en: "Custom kitchen" },
    { src: "assets/photos/chambre-renovee.webp", fr: "Chambre rénovée", en: "Renovated bedroom" },
    { src: "assets/photos/terrasse-bois.webp", fr: "Terrasse bois", en: "Wooden deck" },
    { src: "assets/photos/appliques-parquet.webp", fr: "Appliques & parquet", en: "Wall lights & flooring" },
    { src: "assets/photos/combles.webp", fr: "Combles aménagés", en: "Converted attic" }
  ]
};
