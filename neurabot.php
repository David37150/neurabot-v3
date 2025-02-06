<?php
session_start();

// Informations de connexion à la base de données
$servername = "db5017061512.hosting-data.io";
$username = "dbu2440284";
$password = "Delllled33/";
$dbname = "dbs13730611";

// Créer la connexion
$conn = new mysqli($servername, $username, $password, $dbname);

// Vérifier la connexion
if ($conn->connect_error) {
    die("Erreur : Impossible de se connecter à la base de données. " . $conn->connect_error);
}

?>


<?php include './include/ressources.php'; ?>
<body>
<!-- Top Header -->
<?php include './include/menu.php'; ?>
<style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; }
        h1 { color: #333; }
        #chat-container {text-align: center;margin: 25px;background: white;padding: 20px;border-radius: 10px;box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);}
        input, button { width: 100%; padding: 10px; margin-top: 10px; border-radius: 5px; border: 1px solid #ccc; }
        button { background: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        #response { margin-top: 20px; text-align: left; background: #e9ecef; padding: 10px; border-radius: 5px; }
    </style>

<div class="container-fluid">
    <div class="row align-items-stretch">

        <div class="row align-items-center">
            <!-- Image à gauche (30%) -->
            <div class="col-xs-12 col-sm-12 col-md-0 col-lg-3 col-xl-3 mb-2 text-center">
                <div class="card h-100 p-4">
                    <img src="https://neurainvests.com/img/design/ia-chat.png" alt="NeuraBot Logo" width="100%" style="max-width: 250px;">
                </div>
            </div>

            <!-- Card à droite (70%) -->
            <div class="col-xs-12 col-sm-12 col-md-12 col-lg-9 col-xl-9 mb-2">
                <div class="card h-100 p-4">
                    <h1 class="text-left">NeuraBot - Chat / ADS IA Assistance</h1>
                    <div id="chat-container">
                        <input type="text" id="question" placeholder="Pose ta question ici...">
                        <button onclick="askNeuraBot()">Envoyer</button>
                        <div id="response"></div>
                    </div>
                    <small class="text-right">Le service ADS n'est disponible que pour l'Administrateur du site</small>
                </div>
            </div>
        </div>

    </div>
</div>

    <script>
        function askNeuraBot() {
            let question = document.getElementById("question").value;
            let responseDiv = document.getElementById("response");
            
            if (question.trim() === "") {
                responseDiv.innerHTML = "<p style='color:red;'>Veuillez entrer une question.</p>";
                return;
            }

            responseDiv.innerHTML = "<p>⏳ NeuraBot réfléchit...</p>";

            fetch("https://neurabot.onrender.com/ask?question=" + encodeURIComponent(question))
                .then(response => response.json())
                .then(data => {
                    responseDiv.innerHTML = "<p><strong>Réponse :</strong> " + data.response + "</p>";
                })
                .catch(error => {
                    responseDiv.innerHTML = "<p style='color:red;'>❌ Erreur de connexion à l'API.</p>";
                });
        }
    </script>

<!-- translations -->
<script>
document.addEventListener('DOMContentLoaded', () => {
    // Détecter la langue actuelle depuis l'URL
    const currentLang = new URLSearchParams(window.location.search).get('lang') || 'fr';
    console.log(`Langue actuelle détectée : ${currentLang}`);

    // Charger les traductions dynamiquement
    function loadTranslations(lang) {
        console.log(`Chargement des traductions pour la langue : ${lang}`);
        return fetch(`/pages/translations/${lang}.json`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Impossible de charger les traductions pour ${lang}`);
                }
                return response.json();
            })
            .then(translations => {
                console.log(`Traductions chargées :`, translations);
                return translations;
            })
            .catch(error => {
                console.error('Erreur lors du chargement des traductions :', error);
                return {}; // Retourner un objet vide si le chargement échoue
            });
    }

    // Appliquer les traductions aux éléments ayant des attributs data-translate-key
    function applyTranslations(translations) {
        document.querySelectorAll('[data-translate-key]').forEach(element => {
            const key = element.getAttribute('data-translate-key');
            if (translations[key]) {
                element.textContent = translations[key];
            }
        });
    }

    // Mettre à jour l'URL avec la langue
    function updateUrl(lang) {
        const baseUrl = window.location.origin + window.location.pathname; // URL sans paramètres
        let newUrl = `${baseUrl}?lang=${lang}`;
        history.replaceState(null, '', newUrl); // Met à jour l'URL sans recharger la page
    }

    // Initialisation
    loadTranslations(currentLang).then(translations => {
        applyTranslations(translations);
    });

    // Gérer l'ouverture/fermeture du sélecteur de langue
    const selectedElement = document.querySelector('.selected');
    const optionsParent = document.querySelector('.custom-select');
    const options = document.querySelectorAll('.option');

    selectedElement.addEventListener('click', function () {
        optionsParent.classList.toggle('open');
    });

    // Gérer la sélection de la langue
    options.forEach(option => {
        option.addEventListener('click', function () {
            const value = this.dataset.value;
            const text = this.textContent.trim();
            const imgSrc = this.querySelector('img').src;

            // Mettre à jour le contenu de l'élément sélectionné
            const selectedImg = selectedElement.querySelector('img');
            const selectedText = selectedElement.querySelector('span');

            if (selectedImg) {
                selectedImg.src = imgSrc;
                selectedImg.alt = text;
            } else {
                const img = document.createElement('img');
                img.src = imgSrc;
                img.alt = text;
                img.classList.add('flag-icon');
                selectedElement.prepend(img);
            }

            if (selectedText) {
                selectedText.textContent = text;
            } else {
                const span = document.createElement('span');
                span.textContent = text;
                selectedElement.appendChild(span);
            }

            // Fermer le menu des options
            optionsParent.classList.remove('open');

            // Mettre à jour l'URL proprement
            updateUrl(value);

            // Recharger les traductions
            loadTranslations(value).then(translations => {
                applyTranslations(translations);
            });
        });
    });

    // Fermer les options si on clique en dehors du sélecteur
    document.addEventListener('click', (event) => {
        if (!optionsParent.contains(event.target)) {
            optionsParent.classList.remove('open');
        }
    });
});

</script>

        <!-- JS Links -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script src="https://cdn.datatables.net/1.13.5/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.5/js/dataTables.bootstrap5.min.js"></script>
        <script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>
        <script src="https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jqvmap/1.5.1/jquery.vmap.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jqvmap/1.5.1/maps/jquery.vmap.world.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/jquery.magnific-popup.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/dropzone/5.9.3/min/dropzone.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/audioplayer@0.5.1/dist/audioplayer.min.js"></script>
        <script src="https://neurainvests.com/js/app.js"></script>
        <script src="https://neurainvests.com/js/lineChartPageChart.js"></script>
        <script src="https://neurainvests.com/js/pieChartPageChart.js"></script>
        <script src="https://neurainvests.com/js/columnChartPageChart.js"></script>
        
    </body>
    </html>