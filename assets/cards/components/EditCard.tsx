import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import TextInput from 'components/TextInput';
import AuditInformation from 'components/AuditInformation';
import SelectInput from 'components/SelectInput';

import {gettext} from 'utils';
import {
    CARD_TYPES,
    getCardEditComponent,
} from 'components/cards/utils';
import {Button} from 'components/Buttons';
import CloseButton from 'components/CloseButton';


class EditCard extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any) {
        super(props);
    }

    render() {
        const dashboard = (get(this.props, 'dashboards') || []).find((d: any) => d._id === this.props.card.dashboard);
        const cardType = this.props.card.type || '';
        const CardComponent = getCardEditComponent(cardType);
        const cardTypes: any = CARD_TYPES.filter(
            (card: any) =>  dashboard.cards.includes(card._id)
        ).map((c: any) => ({value: c._id, text: c.text}));

        cardTypes.unshift({value: '', text: '', component: getCardEditComponent('')});

        const cardProps: any = {
            card: this.props.card,
            onChange: this.props.onChange,
            errors: this.props.errors
        };

        if (cardType.includes('navigation')) {
            cardProps.navigations = this.props.navigations;
        } else if (!['4-photo-gallery', '2x2-events'].includes(cardType)) {
            cardProps.products = this.props.products;
        }

        return (
            <div className='list-item__preview' role={gettext('dialog')} aria-label={gettext('Edit Cards')}>
                <div className='list-item__preview-header'>
                    <h3>{this.props.card.label}</h3>
                    <CloseButton onClick={this.props.onClose} />
                </div>
                <AuditInformation item={this.props.card} />
                <form>
                    <div className="list-item__preview-form">
                        <TextInput
                            name='label'
                            label={gettext('Label')}
                            value={this.props.card.label}
                            onChange={this.props.onChange}
                            error={this.props.errors ? this.props.errors.label : null}/>

                        <SelectInput
                            name='type'
                            label={gettext('Type')}
                            value={this.props.card.type}
                            options={cardTypes}
                            onChange={this.props.onChange}
                            error={this.props.errors ? this.props.errors.type : null} />

                        <TextInput
                            name='order'
                            type='number'
                            label={gettext('Order')}
                            value={`${this.props.card.order}`}
                            onChange={this.props.onChange}
                            error={this.props.errors ? this.props.errors.order : null}/>

                        <CardComponent {...cardProps}/>
                    </div>
                    <div className='list-item__preview-footer'>
                        <Button
                            value={gettext('Delete')}
                            variant='secondary'
                            onClick={this.props.onDelete}
                        />
                        <Button
                            value={gettext('Save')}
                            variant='primary'
                            onClick={this.props.onSave}
                        />
                    </div>
                </form>
            </div>
        );
    }
}

EditCard.propTypes = {
    card: PropTypes.object.isRequired,
    onChange: PropTypes.func,
    errors: PropTypes.object,
    products: PropTypes.arrayOf(PropTypes.object),
    navigations: PropTypes.arrayOf(PropTypes.object),
    onSave: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    dashboards:  PropTypes.arrayOf(PropTypes.object),
};

export default EditCard;
