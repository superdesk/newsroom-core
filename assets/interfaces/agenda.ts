interface IPhoneNumber {
    public: boolean;
    number: string;
    usage?: string;
}

export interface IContact {
    _id: string;
    uri: string;
    public: boolean;
    first_name?: string;
    last_name?: string;
    postcode?: string;
    locality?: string;
    website?: string;
    notes?: string;
    organisation?: string;
    mobile?: Array<IPhoneNumber>;
    contact_phone?: Array<IPhoneNumber>;
    contact_email?: string[];
}

export interface ILocation {
    name: string;
    qcode: string;
    location?: {lat: number; lon: number};
    details?: string[];
    address?: {
        area?: string;
        locality?: string;
        country?: string;
        title?: string;
        line?: string[];
        postal_code?: string;
    };
}

export interface IEvent {
    event_contact_info?: Array<IContact>;
    location?: Array<ILocation>;
}

export interface IAgendaItem {
    event?: IEvent;
    location?: IEvent['location'];
}