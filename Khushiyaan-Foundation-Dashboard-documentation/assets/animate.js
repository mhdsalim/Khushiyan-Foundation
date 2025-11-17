// document.addEventListener("DOMContentLoaded", function () {
//     function animateValue(id, start, end, duration) {
//         let obj = document.getElementById(id);
//         if (!obj) return; // safeguard
//         let startTimestamp = null;

//         function step(timestamp) {
//             if (!startTimestamp) startTimestamp = timestamp;
//             const progress = Math.min((timestamp - startTimestamp) / duration, 1);
//             obj.textContent = Math.floor(progress * (end - start) + start);
//             if (progress < 1) {
//                 window.requestAnimationFrame(step);
//             }
//         }
//         window.requestAnimationFrame(step);
//     }

//     function startAnimations() {
//         let participants = document.getElementById("participants-count");
//         let waste = document.getElementById("waste-count");
//         let recycle = document.getElementById("recycle-count");

//         if (participants && waste && recycle) {
//             animateValue("participants-count", 0, 2500, 2000, "+");
//             animateValue("waste-count", 0, 1200, 2000, "kg");
//             animateValue("recycle-count", 0, 900, 2000, "kg");
//         } else {
//             // retry after 300ms if elements are not yet in DOM
//             setTimeout(startAnimations, 300);
//         }
//     }

//     startAnimations();
// });

document.addEventListener("DOMContentLoaded", function () {
    function animateValue(id, start, end, duration, suffix = "") {
        let obj = document.getElementById(id);
        if (!obj) return; // safeguard
        let startTimestamp = null;

        function step(timestamp) {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            let value = Math.floor(progress * (end - start) + start);

            // add suffix while animating
            obj.textContent = value + suffix;

            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        }
        window.requestAnimationFrame(step);
    }

    function startAnimations() {
        let participants = document.getElementById("participants-count");
        let waste = document.getElementById("waste-count");
        let recycle = document.getElementById("recycle-count");

        if (participants && waste && recycle) {
            animateValue("participants-count", 0, 189290, 2000, "");
            animateValue("waste-count", 0, 1300, 2000, "+");
            animateValue("recycle-count", 0, 2.3, 2000, "M+ Kg");
        } else {
            // retry after 300ms if elements are not yet in DOM
            setTimeout(startAnimations, 300);
        }
    }

    startAnimations();
});