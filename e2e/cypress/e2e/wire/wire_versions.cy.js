import {setup, addDefaultResources, addResources} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {WIRE_SEGMENTS} from '../../fixtures/wire';

const Segments = {
    first: WIRE_SEGMENTS.first,
    second: WIRE_SEGMENTS.second,
    third: WIRE_SEGMENTS.third,
};

function version(id) {
    return cy.get(`[data-test-id="wire-version-item"][data-test-value="${id}"]`);
}

function expectBody(segmentNumber) {
    cy.get('#preview-body').should('contain.text', `body of segment ${segmentNumber} of 3`);
}

// clicking between segments/versions in the item detail view must show the
// content of the selected segment, not the originally opened one.
describe('wire - item detail versions', () => {
    beforeEach(() => {
        setup();
        addDefaultResources();
        addResources([{
            resource: 'items',
            use_resource_service: false,
            items: [Segments.first, Segments.second, Segments.third],
        }]);
        NewshubLayout.login('admin@example.com', 'admin');
    });

    it('shows each segment content when navigating versions', () => {
        cy.visit(`/wire?item=${encodeURIComponent(Segments.third._id)}`);
        expectBody(3);

        // switching versions must swap the body in place
        version(Segments.first._id).click();
        expectBody(1);

        // a non-latest next version must still carry its body
        version(Segments.second._id).click();
        expectBody(2);

        version(Segments.third._id).click();
        expectBody(3);
    });
});
