export interface ISeat {
    _id: string;
    name: string;
    description: string;
    section: string;
    max_seats: number;
    assigned_seats: number;
    max_reached: boolean;
}

export interface ISeats {
    [companyId: string]: {
        [productId: string]: ISeat;
    };
}