/**
 * tested on dnd-kit
 */
export function dragAndDrop(draggableElement: Cypress.Chainable<JQuery<HTMLElement>>, dropArea: Cypress.Chainable<JQuery<HTMLElement>>) {
    draggableElement.then(($draggable) => {
        return dropArea.then(($dropArea) => {
            const draggableRect = $draggable[0].getBoundingClientRect();
            const dropAreaRect = $dropArea[0].getBoundingClientRect();
            const deltaX = dropAreaRect.x - draggableRect.x;
            const deltaY = dropAreaRect.y - draggableRect.y;

            draggableElement.mouseMoveBy(deltaX, deltaY);
        });
    });
}
