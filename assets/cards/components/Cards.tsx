import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {gettext} from 'utils';

import {
    cancelEdit,
    deleteCard,
    editCard,
    newCard,
    postCard,
    selectCard,
    setError,
} from '../actions';
import {searchQuerySelector} from 'search/selectors';

import EditCard from './EditCard';
import CardList from './CardList';
import SearchResults from 'search/components/SearchResults';

class Cards extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any, context: any) {
        super(props, context);

        this.isFormValid = this.isFormValid.bind(this);
        this.save = this.save.bind(this);
        this.deleteCard = this.deleteCard.bind(this);
    }

    isFormValid() {
        let valid = true;
        const errors: any = {};

        if (!this.props.cardToEdit.label) {
            errors.label = [gettext('Please provide card label')];
            valid = false;
        }

        if (this.props.cardToEdit.type === '2x2-events' &&
          !this.props.cardToEdit.config.events[0].startDate) {
            errors.event_0_startDate = [gettext('Please provide start date')];
            valid = false;
        }

        this.props.dispatch(setError(errors));
        return valid;
    }

    save(event: any) {
        event.preventDefault();

        if (!this.isFormValid()) {
            return;
        }

        this.props.saveCard();
    }

    deleteCard(event: any) {
        event.preventDefault();

        if (confirm(gettext('Would you like to delete card: {{label}}', {label: this.props.cardToEdit.label}))) {
            this.props.deleteCard();
        }
    }

    render() {
        const progressStyle: any = {width: '25%'};
        const cardFilter = (card: any) =>  !this.props.activeDashboard ||
            get(card, 'dashboard', 'newsroom') === this.props.activeDashboard;

        return (
            <div className="flex-row">
                {(this.props.isLoading ?
                    <div className="col d">
                        <div className="progress">
                            <div className="progress-bar" style={progressStyle} />
                        </div>
                    </div>
                    :
                    <div className="flex-col flex-column">
                        {this.props.activeQuery && (
                            <SearchResults
                                totalItems={this.props.totalCards}
                                totalItemsLabel={this.props.activeQuery}
                            />
                        )}
                        <CardList
                            cards={this.props.cards.filter(cardFilter)}
                            products={this.props.products}
                            onClick={this.props.selectCard}
                            activeCardId={this.props.activeCardId} />
                    </div>
                )}
                {this.props.cardToEdit &&
                    <EditCard
                        card={this.props.cardToEdit}
                        onChange={this.props.editCard}
                        errors={this.props.errors}
                        onSave={this.save}
                        onClose={this.props.cancelEdit}
                        onDelete={this.deleteCard}
                        products={this.props.products}
                        navigations={this.props.navigations}
                        dashboards={this.props.dashboards}
                    />
                }
            </div>
        );
    }
}

Cards.propTypes = {
    cards: PropTypes.arrayOf(PropTypes.object),
    cardToEdit: PropTypes.object,
    activeCardId: PropTypes.string,
    selectCard: PropTypes.func,
    editCard: PropTypes.func,
    saveCard: PropTypes.func,
    deleteCard: PropTypes.func,
    newCard: PropTypes.func,
    cancelEdit: PropTypes.func,
    isLoading: PropTypes.bool,
    activeQuery: PropTypes.string,
    totalCards: PropTypes.number,
    errors: PropTypes.object,
    dispatch: PropTypes.func,
    products: PropTypes.arrayOf(PropTypes.object),
    navigations: PropTypes.arrayOf(PropTypes.object),
    activeDashboard: PropTypes.string.isRequired,
    dashboards: PropTypes.arrayOf(PropTypes.object),
};

const mapStateToProps = (state: any) => ({
    cards: state.cards.map((id: any) => state.cardsById[id]),
    cardToEdit: state.cardToEdit,
    activeCardId: state.activeCardId,
    isLoading: state.isLoading,
    activeQuery: searchQuerySelector(state),
    totalCards: state.totalCards,
    errors: state.errors,
    products: state.products,
    navigations: state.navigations,
    activeDashboard: state.dashboards.active,
    dashboards: state.dashboards.list,
});

const mapDispatchToProps = (dispatch: any) => ({
    selectCard: (_id: any) => dispatch(selectCard(_id)),
    editCard: (event: any) => dispatch(editCard(event)),
    saveCard: () => dispatch(postCard()),
    deleteCard: () => dispatch(deleteCard()),
    newCard: () => dispatch(newCard()),
    cancelEdit: (event: any) => dispatch(cancelEdit(event)),
    dispatch: dispatch,
});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(Cards);

export default component;
