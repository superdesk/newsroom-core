import * as React from 'react';
import {connect} from 'react-redux';

import {IArticle, IDashboardCard, IListConfig, IPublicAppState} from 'interfaces';
import {IModalState} from 'reducers';

import {gettext, getConfig} from 'utils';
import {listConfigSelector} from 'ui/selectors';
import {renderModal} from 'actions';
import {fetchCardExternalItems} from 'home/actions';

import {DashboardPanels} from 'home/components/DashboardPanels';
import Modal from 'components/Modal';
import {HTMLContent} from 'components/HTMLContent';

interface IStateProps {
    cards: Array<IDashboardCard>;
    itemsByCard: {[cardId: string]: Array<IArticle>};
    listConfig: IListConfig;
    modal?: IModalState;
}

interface IDispatchProps {
    fetchCardExternalItems(cardId: IDashboardCard['_id'], cardLabel: IDashboardCard['label']): void;
    renderModal(modal: string, nextUrl: string): void;
}

type IProps = IStateProps & IDispatchProps;
const RESTRICTED_ACCESS_MODAL_NAME = 'restrictedAccessModal';

const PublicAppComponent: React.FC<IProps> = ({
    cards,
    itemsByCard,
    listConfig,
    fetchCardExternalItems,
    modal,
    renderModal,
}) => (
    <React.Fragment>
        <section className="content-main d-block py-4 px-2 p-md-3 p-lg-4">
            <div className="container-fluid">
                <DashboardPanels
                    cards={cards.filter((card) => card.dashboard === 'newsroom')}
                    activeCard={undefined}
                    itemsByCard={itemsByCard}
                    listConfig={listConfig}
                    fetchCardExternalItems={fetchCardExternalItems}
                    openItem={(item) => {
                        renderModal(RESTRICTED_ACCESS_MODAL_NAME, `/wire?item=${item._id}`);
                    }}
                    onMoreNewsClicked={(event) => {
                        event.preventDefault();
                        renderModal(RESTRICTED_ACCESS_MODAL_NAME, (event.target as HTMLAnchorElement).href);
                    }}
                />
            </div>
        </section>
        {modal?.modal !== RESTRICTED_ACCESS_MODAL_NAME ? null : (
            (
                <Modal
                    title={gettext('This action requires you to log in!')}
                    footer={() => (
                        <div className="modal-footer">
                            {getConfig('show_user_register') != true ? null : (
                                <a
                                    type="button"
                                    className="nh-button nh-button--secondary"
                                    href="/signup"
                                >
                                    {gettext('Register')}
                                </a>
                            )}
                            <a
                                type="button"
                                className="nh-button nh-button--primary"
                                href={modal.data}
                            >
                                {gettext('Login')}
                            </a>
                        </div>
                    )}
                >
                    <HTMLContent text={window.restrictedActionModalBody} />
                </Modal>
            )
        )}
    </React.Fragment>
);

const mapStateToProps = (state: IPublicAppState): IStateProps => ({
    cards: state.cards,
    itemsByCard: state.itemsByCard,
    listConfig: listConfigSelector(state),
    modal: state.modal,
});

const mapDispatchToProps: IDispatchProps = {
    fetchCardExternalItems,
    renderModal,
};

export const PublicApp = connect<
    IStateProps,
    IDispatchProps,
    {},
    IPublicAppState
>(mapStateToProps, mapDispatchToProps)(PublicAppComponent);
