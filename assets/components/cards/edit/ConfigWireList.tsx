import * as React from 'react';

import {IDashboardCard, IProduct} from 'interfaces';
import {gettext} from 'utils';

import SelectInput from 'components/SelectInput';
import TextInput from 'components/TextInput';

interface IProps {
    card: IDashboardCard;
    onChange(event: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>): void;
    errors: {[key: string]: Array<string>};
    products: Array<IProduct>;
}

export class ConfigWireList extends React.PureComponent<IProps> {

    render() {
        const productOptions = [{value: '', text: ''}].concat(
            this.props.products
                .filter((product) => product.product_type === 'wire')
                .map((product) => ({value: product._id, text: product.name}))
        );

        return (
            <React.Fragment>
                <SelectInput
                    key="product"
                    name="product"
                    label={gettext('Product')}
                    value={this.props.card.config.product}
                    options={productOptions}
                    onChange={this.props.onChange}
                    error={this.props.errors?.product ?? null}
                />
                <TextInput
                    key="size"
                    name="size"
                    type="number"
                    label={gettext('Number of items')}
                    value={(this.props.card.config.size ?? 4).toString(10)}
                    onChange={this.props.onChange}
                    error={this.props.errors?.size ?? null}
                />
            </React.Fragment>
        );
    }
}
