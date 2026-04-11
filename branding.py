BRANDING = {
    "modo": "garciabanchs",
    "mostrar_bio": True,
    "mostrar_libros": True,
    "mostrar_contacto": True,

    "garciabanchs": {
        "titulo": "Acerca del autor",
        "nombre": "Ángel García Banchs",
        "subtitulo": "Economista, profesor universitario y consultor financiero especializado en creación de patrimonio y planificación financiera a largo plazo.",
        "descripcion": (
            "Esta herramienta de análisis financiero fue desarrollada para ayudar a transformar "
            "documentos comerciales dispersos en perspectivas financieras más claras, mejorando "
            "la toma de decisiones para las PYME."
        ),

        # 👇 ASEGÚRATE de que este archivo exista en /static
        "imagen_url": "https://angelgarciabanchs.com/wp-content/uploads/2025/06/imagen-circular.png",

        "contacto_texto": "Contáctame",
        "contacto_url": "https://linktr.ee/garciabanchs",

        "libros": [
            {
                "titulo": "CAMINO A LA RIQUEZA: Desmontando falacias y revelando la ruta",
                "url": "https://amzn.eu/d/0gYgZQfp",

                # opcional (backend)
                "portada_local": "static/camino-a-la-riqueza.jpg",

                # 👇 ESTE ES EL QUE USA EL HTML
                "portada_html": "/static/camino-a-la-riqueza.jpg"
            },
            {
                "titulo": "The Artificial Intelligence Millionaire",
                "url": "https://amzn.eu/d/00BhXvMF",

                "portada_local": "static/the-artificial-intelligence-millionaire.jpg",
                "portada_html": "/static/the-artificial-intelligence-millionaire.jpg"
            }
        ]
    }
}
