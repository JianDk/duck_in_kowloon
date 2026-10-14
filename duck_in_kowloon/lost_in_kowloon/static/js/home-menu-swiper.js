(function () {
  function getNearestIndex(cards, scroller) {
    const center = scroller.scrollLeft + scroller.clientWidth / 2;
    let nearestIndex = 0;
    let nearestDistance = Number.POSITIVE_INFINITY;

    cards.forEach(function (card, index) {
      const cardCenter = card.offsetLeft + card.offsetWidth / 2;
      const distance = Math.abs(cardCenter - center);
      if (distance < nearestDistance) {
        nearestDistance = distance;
        nearestIndex = index;
      }
    });

    return nearestIndex;
  }

  function goToCard(cards, scroller, index) {
    if (!cards.length) return;
    const safeIndex = Math.max(0, Math.min(index, cards.length - 1));
    cards[safeIndex].scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" });
  }

  function initMenuSwiper() {
    const scroller = document.querySelector("[data-menu-scroller]");
    const prevButton = document.querySelector("[data-menu-prev]");
    const nextButton = document.querySelector("[data-menu-next]");

    if (!scroller || !prevButton || !nextButton) return;

    const cards = Array.prototype.slice.call(scroller.querySelectorAll("[data-menu-card]"));
    if (!cards.length) return;

    prevButton.addEventListener("click", function () {
      const current = getNearestIndex(cards, scroller);
      goToCard(cards, scroller, current - 1);
    });

    nextButton.addEventListener("click", function () {
      const current = getNearestIndex(cards, scroller);
      goToCard(cards, scroller, current + 1);
    });

    scroller.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      const current = getNearestIndex(cards, scroller);
      goToCard(cards, scroller, current + (event.key === "ArrowRight" ? 1 : -1));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMenuSwiper);
  } else {
    initMenuSwiper();
  }
})();
